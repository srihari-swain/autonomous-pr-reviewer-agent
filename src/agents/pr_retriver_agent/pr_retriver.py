
from typing import Dict
from src.tools.github_mcp_tool import fetch_pr_data

async def pr_retriever_agent(repo_owner: str, repo_name: str, pr_number: int) -> Dict:
    pr_raw = await fetch_pr_data(repo_owner, repo_name, pr_number)
    pr_info = {
        "pr_number": pr_raw.get("number") or pr_number,
        "pr_title": pr_raw.get("title") or "",
        "pr_description": pr_raw.get("body") or "",
        "pr_author": pr_raw.get("user", {}).get("login") or "",
        "pr_state": pr_raw.get("state") or "",
        "pr_url": pr_raw.get("html_url") or "",
        "pr_files": [],
        "pr_commits": [],
        "pr_diff": pr_raw.get("pr_diff", ""),
    }

    # Files
    for file in pr_raw.get("pr_files", []):
        pr_info["pr_files"].append({
            "filename": file.get("filename", ""),
            "status": file.get("status", ""),
            "additions": file.get("additions", 0),
            "deletions": file.get("deletions", 0),
        })

    # Commits
    for commit in pr_raw.get("pr_commits", []):
        pr_info["pr_commits"].append({
            "sha": commit.get("sha", ""),
            "message": commit.get("commit", {}).get("message", commit.get("message", "")),
            "author": (
                commit.get("commit", {}).get("author", {}).get("name")
                or commit.get("author", "")
                or ""
            ),
        })

    return pr_info
