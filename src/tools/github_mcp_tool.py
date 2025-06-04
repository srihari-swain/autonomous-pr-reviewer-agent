# github_mcp.py

import os
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()
# Load environment variables from .env file
MCP_SERVER_PATH = "src/comms/server/github-mcp-server/github-mcp-server"
GITHUB_PAT = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")

def get_mcp_env():
    return {
        "GITHUB_PERSONAL_ACCESS_TOKEN": GITHUB_PAT,
        "GITHUB_TOOLSETS": "repos,issues,pull_requests,code_security"
    }

async def get_tools():
    client = MultiServerMCPClient({
        "github": {
            "command": MCP_SERVER_PATH,
            "args": ["stdio"],
            "env": get_mcp_env()
        }
    })
    await client.__aenter__()
    tools = client.get_tools()
    return client, tools

async def list_prs(repo_owner, repo_name, state="open"):
    client, tools = await get_tools()
    list_prs_tool = next((t for t in tools if t.name == 'list_pull_requests'), None)
    prs = []
    if list_prs_tool:
        result = await list_prs_tool.ainvoke({
            "owner": repo_owner,
            "repo": repo_name,
            "state": state,
            "per_page": 100
        })
        import json
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except Exception:
                pass
        if isinstance(result, dict) and "data" in result:
            result = result["data"]
        if isinstance(result, list):
            prs = result
    await client.__aexit__(None, None, None)
    return prs

async def fetch_pr_data(repo_owner, repo_name, pr_number):
    import json
    client, tools = await get_tools()
    get_pr_tool = next((t for t in tools if t.name == 'get_pull_request'), None)
    get_pr_files_tool = next((t for t in tools if t.name == 'get_pull_request_files'), None)
    get_pr_diff_tool = next((t for t in tools if t.name == 'get_pull_request_diff'), None)
    list_commits_tool = next((t for t in tools if t.name == 'list_commits'), None)
    pr_data = {}

    # PR details
    if get_pr_tool:
        pr_info = await get_pr_tool.ainvoke({
            "owner": repo_owner,
            "repo": repo_name,
            "pullNumber": pr_number,
            "state": "open"
        })
        if isinstance(pr_info, str):
            try:
                pr_info = json.loads(pr_info)
            except Exception:
                pass
        if isinstance(pr_info, dict):
            pr_data.update(pr_info)

    # PR files
    if get_pr_files_tool:
        files = await get_pr_files_tool.ainvoke({
            "owner": repo_owner,
            "repo": repo_name,
            "pullNumber": pr_number,
            "state": "open"
        })
        if isinstance(files, str):
            try:
                files = json.loads(files)
            except Exception:
                pass
        if isinstance(files, dict) and "data" in files:
            files = files["data"]
        if isinstance(files, list):
            pr_data["pr_files"] = files

    # PR diff
    if get_pr_diff_tool:
        diff = await get_pr_diff_tool.ainvoke({
            "owner": repo_owner,
            "repo": repo_name,
            "pullNumber": pr_number,
            "state": "open"
        })
        if isinstance(diff, str):
            pr_data["pr_diff"] = diff[:5000]

    # PR commits
    pr_data["pr_commits"] = []
    if list_commits_tool:
        commits = await list_commits_tool.ainvoke({
            "owner": repo_owner,
            "repo": repo_name,
            "pullNumber": pr_number,
            "state": "open"
        })
        if isinstance(commits, str):
            try:
                commits = json.loads(commits)
            except Exception:
                pass
        if isinstance(commits, dict) and "data" in commits:
            commits = commits["data"]
        if isinstance(commits, list):
            pr_data["pr_commits"] = commits

    await client.__aexit__(None, None, None)
    return pr_data
