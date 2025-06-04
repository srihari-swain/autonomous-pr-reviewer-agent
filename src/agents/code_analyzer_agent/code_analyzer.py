"""
Simplified Code Understanding Agent

Analyzes PR file changes to:
1. Summarize code changes
2. Identify risky coding practices  
3. Provide improvement recommendations
"""

import os
import re
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("WARNING: OPENAI_API_KEY is not set in the .env file.")

# Prompts for different file types
ANALYZE_CHANGES_PROMPT = """
You are an expert code reviewer. Analyze the following code changes and provide:

File: {filename}
Changes: +{additions}/-{deletions}

```diff
{file_diff}
```

Please provide:

## Summary of Changes
- What was changed in this file?
- Purpose of these changes?

## Code Quality Issues
- Any bugs or logical errors?
- Poor coding practices identified?
- Security vulnerabilities?

## Risky Practices Found
- High risk: Could cause failures/security issues
- Medium risk: Could lead to bugs/maintenance issues  
- Low risk: Style/minor improvements needed

## Recommendations  
- Critical fixes needed before merge
- Suggested improvements
- Testing recommendations

Keep the analysis focused and actionable.
"""

def extract_file_changes(pr_data: Dict) -> Dict[str, Dict]:
    """Extract individual file changes from PR diff."""
    if not pr_data.get("pr_diff"):
        return {}
    
    full_diff = pr_data["pr_diff"]
    files_data = pr_data.get("pr_files", [])
    
    # Map filenames to metadata
    file_metadata = {file.get("filename"): file for file in files_data}
    
    # Split diff by files using regex
    file_pattern = r'diff --git a/(.*?) b/(.*?)\n'
    file_splits = re.split(file_pattern, full_diff)
    
    file_changes = {}
    
    for i in range(1, len(file_splits), 3):
        if i + 2 < len(file_splits):
            filename = file_splits[i + 1]  # Use 'after' filename
            diff_content = file_splits[i + 2]
            
            metadata = file_metadata.get(filename, {})
            
            diff_header = f"diff --git a/{file_splits[i]} b/{filename}" + "\n" + diff_content
            
            file_changes[filename] = {
                "filename": filename,
                "additions": metadata.get("additions", 0),
                "deletions": metadata.get("deletions", 0),
                "diff": diff_header.strip()
            }
    
    return file_changes

async def code_analyzer(pr_data: Dict) -> str:
    """Analyze changes in a single file."""
    file_changes = extract_file_changes(pr_data)
    filename = file_changes.get("filename", "Unknown")
    prompt_data = {
        "filename": filename,
        "additions": file_changes.get("additions", 0),
        "deletions": file_changes.get("deletions", 0),
        "file_diff": file_changes.get("diff", "No diff available")
    }
    prompt_template = ANALYZE_CHANGES_PROMPT
    prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = (
        prompt 
        | ChatOpenAI(model="gpt-4o", temperature=0, api_key=OPENAI_API_KEY)
        | StrOutputParser()
    )
    
    return await chain.ainvoke(prompt_data)
