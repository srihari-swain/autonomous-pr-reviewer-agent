import re
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


from src.utils.config_loader import read_base_config
from src.orchestrator.agent_orchestrator import create_pr_workflow  
CONFIG = read_base_config()     

# Create FastAPI app with config
app = FastAPI(
    title=CONFIG["API"]["title"],
    description=CONFIG["API"]["description"],
    version=CONFIG["API"]["version"],
    docs_url=CONFIG["API"]["docs_url"],
    redoc_url=CONFIG["API"]["redoc_url"]
)

# Add CORS middleware using config
app.add_middleware(
    CORSMiddleware,                                                     
    allow_origins=CONFIG["API"]["allow_origins"],
    allow_credentials=CONFIG["API"]["allow_credentials"],
    allow_methods=CONFIG["API"]["allow_methods"],
    allow_headers=CONFIG["API"]["allow_headers"],
)


class PRLinkRequest(BaseModel):
    github_link: str

def parse_github_pr_url(url: str):
    """
    Parses a GitHub PR URL and returns (owner, repo, pr_number)
    Accepts URL with or without https:// prefix.
    """
    pattern = r"^(https://)?github\.com/([^/]+)/([^/]+)/pull/(\d+)$"
    match = re.match(pattern, url)
    if match:
        _, owner, repo, pr_number = match.groups()
        return owner, repo, int(pr_number)
    raise ValueError("Invalid GitHub PR URL format.")

def strip_ansi_codes(text):
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)

@app.post("/review-pr")
async def analyze_pr(req: PRLinkRequest):
    try:
        repo_owner, repo_name, pr_number = parse_github_pr_url(req.github_link)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    state = {
        "repo_owner": repo_owner,
        "repo_name": repo_name,
        "pr_number": pr_number,
        "messages": [{
            "role": "system",
            "content": f"Starting PR analysis for {repo_owner}/{repo_name} PR #{pr_number}"
        }]
    }

    workflow = create_pr_workflow()
    try:
        result = await workflow.ainvoke(state)
        summary = result.get("review_summary", "No summary available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow error: {str(e)}")

    return {"final_review_summary": strip_ansi_codes(summary)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)

