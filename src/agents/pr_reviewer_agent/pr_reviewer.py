import json
import re
from typing import Dict, List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

# Prompt for generating individual review comments
GENERATE_COMMENTS_PROMPT = """
You are an expert PR (GitHub pull request) reviewer generating helpful, specific PR comments from a code analysis.

Code Analysis:
{code_analysis}

Guidelines:
- Be specific and actionable
- Focus on key issues first
- Suggest improvements or fixes
- Be constructive and professional
- Use GitHub Markdown formatting

Return a JSON array of comment objects. Each object must contain:
- content (Markdown string)
- file_path (nullable string)
- line_number (nullable integer)
- comment_type: "suggestion", "issue", "praise", or "question"
- severity (nullable): "critical", "major", "minor", "trivial"

IMPORTANT: Only output the JSON array, with no explanation or extra text.

Example:
[
  {{
    "content": "Consider checking for token expiration to improve security.",
    "file_path": "auth/jwt.py",
    "line_number": 58,
    "comment_type": "issue",
    "severity": "major"
  }}
]
"""

def extract_json_array(text: str) -> Optional[str]:
    """
    Extracts the first JSON array from a string using regex.
    """
    match = re.search(r'(\[\s*{.*?}\s*\])', text, re.DOTALL)
    return match.group(1) if match else None

async def generate_pr_comments(pr_data: Dict, analysis_result: str) -> List[Dict]:
    """
    Generate review comments from analysis.

    Args:
        pr_data: (ignored) Placeholder for interface compatibility.
        analysis_result: Output from code analysis.

    Returns:
        List of comment dicts.
    """
    prompt = ChatPromptTemplate.from_template(GENERATE_COMMENTS_PROMPT)
    chain = prompt | ChatOpenAI(model="gpt-4o", temperature=0.2) | StrOutputParser()

    comments_str = None  # Predefine for error handling
    try:
        comments_str = await chain.ainvoke({"code_analysis": analysis_result})
        # print(f"[DEBUG] Raw LLM output: {comments_str!r}")

        if not comments_str or not comments_str.strip():
            raise ValueError("LLM returned empty output.")

        try:
            comments = json.loads(comments_str)
        except json.JSONDecodeError:
            # Try to extract JSON array from the output
            extracted = extract_json_array(comments_str)
            if extracted:
                comments = json.loads(extracted)
            else:
                raise

        if isinstance(comments, dict) and 'comments' in comments:
            comments = comments['comments']

    except Exception as e:
        print(f"[WARN] Failed to generate comments: {e}")
        comments = [{
            "content": comments_str if comments_str else "Could not parse comment output.",
            "file_path": None,
            "line_number": None,
            "comment_type": "comment",
            "severity": None
        }]

    return comments




