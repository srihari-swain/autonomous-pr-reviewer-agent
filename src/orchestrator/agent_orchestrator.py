import os
import asyncio
from dotenv import load_dotenv
from langgraph.types import Command
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Optional, Dict, List, Any, Literal

# Import your existing components
from src.schema.schema import PRState
from src.utils.config_loader import read_base_config
from src.agents.pr_retriver_agent.pr_retriver import pr_retriever_agent
from src.tools.github_mcp_tool import list_prs
from src.agents.pr_reviewer_agent.pr_reviewer import generate_pr_comments
from src.agents.code_analyzer_agent.code_analyzer import code_analyzer
from src.agents.decision_maker_agent.decision_maker import run_react_agent

# ---------- COLORS FOR OUTPUT ----------
def color_block(text, color_code):
    return f"{color_code}{text}\033[0m"

COLORS = read_base_config()["COLORS"]   

# ---------- ENVIRONMENT ----------
load_dotenv()

REPO_OWNER = "artkulak"
REPO_NAME = "repo2file"

# ---------- AGENT NODES WITH FULL OUTPUT COLOR ----------

async def fetch_node(state: PRState) -> Command[Literal["supervisor"]]:
    pr_data = await pr_retriever_agent(
        repo_owner=state["repo_owner"],
        repo_name=state["repo_name"],
        pr_number=state["pr_number"]
    )
    # Determine if any .py files are changed
    pr_files = pr_data.get("pr_files", [])
    has_code_changes = any(f.get("filename", "").endswith(".py") for f in pr_files)

    output = []
    output.append("\n======== PR RETRIEVER AGENT ========")
    output.append(print_pr_structured(pr_data, return_str=True))
    output.append(f"Has code changes (.py files): {has_code_changes}")
    print(color_block('\n'.join(output), COLORS["fetch"]))

    return Command(
        update={"pr_data": pr_data, "step": "fetch", "has_code_changes": has_code_changes},
        goto="supervisor"
    )

async def analyze_node(state: PRState) -> Command[Literal["supervisor"]]:
    pr_data = state.get("pr_data", {})
    result_sub_state = await code_analyzer(pr_data)
    output = []
    output.append("\n======== CODE ANALYZER AGENT ========")
    output.append(result_sub_state)
    print(color_block('\n'.join(output), COLORS["analyze"]))
    return Command(
        update={
            "analysis": result_sub_state,
            "step": "analyze"
        },
        goto="supervisor"
    )

async def comment_node(state: PRState) -> Command[Literal["supervisor"]]:
    try:
        comments = await generate_pr_comments(state["pr_data"], state.get("analysis"))
        output = []
        output.append("\n======== PR REVIEWER AGENT ========")

        for comment in comments:
            output.append(f"- {comment['comment_type'].upper()} [{comment.get('file_path')}:{comment.get('line_number')}]")
            output.append(f"  {comment['content']}\n")
        print(color_block('\n'.join(output), COLORS["comment"]))
    except Exception as e:
        print(color_block(f"Error generating comments: {e}", COLORS["error"]))
        comments = []
    return Command(
        update={
            "comments": comments,
            "step": "comment"
        },
        goto="supervisor"
    )

async def react_node(state: PRState) -> Command[Literal["supervisor", END]]:
    code_analysis = state.get("analysis", "")
    comments = state.get("comments", [])

    decision_message = await run_react_agent(code_analysis, comments)
    # Color green if merge, red if not
    if "YES, it is safe to merge" in decision_message:
        color = COLORS["merge_green"]
    elif "NO, do not merge" in decision_message:
        color = COLORS["merge_red"]
    else:
        color = COLORS["react"]
    print(color_block(f"\n[REACT AGENT]\n{decision_message}", color))
    return Command(
        update={"merge_decision": decision_message, "step": "react"},
        goto="supervisor"
    )

async def supervisor_node(state: PRState) -> Command[Literal["fetch", "analyze", "comment", "react", END]]:
    current_step = state.get("step")
    has_code_changes = state.get("has_code_changes", False)
    output = []
    output.append("\n======== SUPERVISOR NODE ========")

    if current_step is None:
        output.append("[Supervisor] Starting workflow. Routing to PR RETRIEVER agent.")
        print(color_block('\n'.join(output), COLORS["supervisor"]))
        return Command(update={}, goto="fetch")

    elif current_step == "fetch":
        output.append("[Supervisor] Data fetched.")
        if has_code_changes:
            output.append("Code changes detected. Routing to CODE ANALYZER agent.")
            next_step = "analyze"
        else:
            output.append("No code changes detected. Routing directly to PR REVIEWER agent.")
            next_step = "comment"
        print(color_block('\n'.join(output), COLORS["supervisor"]))
        return Command(update={}, goto=next_step)

    elif current_step == "analyze":
        output.append("[Supervisor] Analysis complete. Routing to PR REVIEWER agent.")
        print(color_block('\n'.join(output), COLORS["supervisor"]))
        return Command(update={}, goto="comment")

    elif current_step == "comment":
        output.append("[Supervisor] Comments generated.")
        pr_data = state.get("pr_data", {})
        comments = state.get("comments", [])
        analysis = state.get("analysis", "No code analysis for non-code changes.")

        if has_code_changes:
            output.append("Code changes present, routing to DECISION MAKER agent.")
            print(color_block('\n'.join(output), COLORS["supervisor"]))
            return Command(update={}, goto="react")
        else:
            output.append("No code changes, ending workflow with final summary.")
            # Build final summary for non-code changes
            summary = []
            summary.append("\n======== FINAL REVIEW SUMMARY ========")
            summary.append("\n--- PR DETAILS ---")
            summary.append(print_pr_structured(pr_data, return_str=True))
            summary.append("\n--- REVIEW COMMENTS ---")
            for comment in comments:
                summary.append(f"- {comment['comment_type'].upper()} [{comment.get('file_path')}:{comment.get('line_number')}]")
                summary.append(f"  {comment['content']}\n")
            summary.append("\n--- MERGE DECISION ---")
            summary.append(color_block("After reviewing your pull request, I am happy to inform you that the changes have been successfully reviewed and are ready to be merged.", COLORS["merge_green"]))
            summary.append("====================================\n")

            print(color_block('\n'.join(output), COLORS["supervisor"]))
            return Command(update={"review_summary": '\n'.join(summary)}, goto=END)

    elif current_step == "react":
        pr_data = state.get("pr_data", {})
        analysis = state.get("analysis", "No analysis available.")
        comments = state.get("comments", [])
        merge_decision = state.get("merge_decision", "")
        if "YES, it is safe to merge" in merge_decision:
            merge_color = COLORS["merge_green"]
        elif "NO, do not merge" in merge_decision:
            merge_color = COLORS["merge_red"]
        else:
            merge_color = COLORS["react"]
        summary = []
        summary.append("\n======== FINAL REVIEW SUMMARY ========")
        summary.append("\n--- PR DETAILS ---")
        summary.append(print_pr_structured(pr_data, return_str=True))
        summary.append("\n--- CODE ANALYSIS ---")
        summary.append(analysis)
        summary.append("\n--- REVIEW COMMENTS ---")
        for comment in comments:
            summary.append(f"- {comment['comment_type'].upper()} [{comment.get('file_path')}:{comment.get('line_number')}]")
            summary.append(f"  {comment['content']}\n")
        summary.append("\n--- MERGE DECISION ---")
        summary.append(color_block(merge_decision, merge_color))
        summary.append("====================================\n")
        print(color_block('\n'.join(output), COLORS["supervisor"]))
        return Command(update={"review_summary": '\n'.join(summary)}, goto=END)

    else:
        output.append(f"[Supervisor] Unknown step: {current_step}. Ending workflow.")
        print(color_block('\n'.join(output), COLORS["error"]))
        return Command(update={}, goto=END)

def create_pr_workflow():
    workflow = StateGraph(PRState)
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("fetch", fetch_node)
    workflow.add_node("analyze", analyze_node)
    workflow.add_node("comment", comment_node)
    workflow.add_node("react", react_node)
    workflow.add_edge(START, "supervisor")
    workflow.add_edge("fetch", "supervisor")
    workflow.add_edge("analyze", "supervisor")
    workflow.add_edge("comment", "supervisor")
    workflow.add_edge("react", "supervisor")
    workflow.set_entry_point("supervisor")
    return workflow.compile()

def print_pr_structured(pr: Dict, return_str=False):
    lines = []
    lines.append("======== PR DETAILS ========")
    lines.append(f"PR #{pr.get('pr_number')}: {pr.get('pr_title', 'Unknown')}")
    lines.append(f"Author: {pr.get('pr_author', 'Unknown')}")
    lines.append(f"State: {pr.get('pr_state', 'Unknown')}")
    lines.append(f"URL: {pr.get('pr_url', '')}")
    lines.append(f"\nDescription:\n{pr.get('pr_description', '')}\n")
    lines.append("--- FILES CHANGED ---")
    for f in pr.get("pr_files", []):
        lines.append(f"- {f.get('filename', '')} ({f.get('status', '')}) [+{f.get('additions', 0)}/-{f.get('deletions', 0)}]")
    lines.append("\n--- COMMITS ---")
    for c in pr.get("pr_commits", []):
        sha_short = c.get('sha','')[:7]
        author = c.get('author','')
        msg_line = c.get('message','').splitlines()[0] if c.get('message') else ''
        lines.append(f"- {sha_short} by {author}: {msg_line}")
    if pr.get("pr_diff"):
        lines.append("\n--- DIFF (First 200 chars) ---")
        lines.append(pr["pr_diff"][:200])
    lines.append("============================\n")
    if return_str:
        return '\n'.join(lines)
    print('\n'.join(lines))

async def get_latest_open_pr_number(repo_owner, repo_name):
    prs = await list_prs(repo_owner, repo_name, state="open")
    if not prs:
        print(color_block(f"No open PRs found in {repo_owner}/{repo_name}", COLORS["error"]))
        return None
    return sorted(
        prs,
        key=lambda pr: pr.get("updated_at", "") or pr.get("created_at", "") or pr.get("number", 0),
        reverse=True
    )[0].get("number")

async def run_workflow():
    pr_number = await get_latest_open_pr_number(REPO_OWNER, REPO_NAME)
    if not pr_number:
        print(color_block("No open PR to analyze.", COLORS["error"]))
        return
    state = {
        "repo_owner": REPO_OWNER,
        "repo_name": REPO_NAME,
        "pr_number": pr_number,
        "messages": [{
            "role": "system",
            "content": f"Starting PR analysis for {REPO_OWNER}/{REPO_NAME} PR #{pr_number}"
        }]
    }
    workflow = create_pr_workflow()
    result = await workflow.ainvoke(state)
    print(result.get("review_summary", "No summary available"))

if __name__ == "__main__":
    asyncio.run(run_workflow())