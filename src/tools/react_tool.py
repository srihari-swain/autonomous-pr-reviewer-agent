from langchain_core.tools import tool

def merge_decision_tool(code_analysis: str, review_comments: str) -> str:
    """
    Decide if the PR should be merged into master, given code analysis and review comments.
    Returns a message with merge decision, rationale, and risk level (high, medium, low).
    """
    code_lower = code_analysis.lower()
    comments_lower = review_comments.lower()

    # High risk conditions
    if "security" in code_lower or "critical bug" in comments_lower or "security" in comments_lower:
        return "NO, do not merge. There are potential security or critical issues that need resolution. Risk level: HIGH."

    # Medium risk conditions
    if "bug" in comments_lower or "potential issue" in comments_lower:
        return "NO, do not merge. Some issues need to be fixed. Risk level: MEDIUM."

    # Low risk / good to merge conditions
    if "looks good" in comments_lower or "no issues found" in code_lower:
        return "YES, it is safe to merge. No critical problems were detected. Risk level: LOW."

    # Default cautious fallback
    return "NO, do not merge. Unable to confidently assess the PR. Risk level: MEDIUM."
