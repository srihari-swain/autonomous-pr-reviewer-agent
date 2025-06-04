from typing import TypedDict, Optional, Dict, List, Any, Literal

class PRState(TypedDict, total=False):
    repo_owner: str
    repo_name: str
    pr_number: int
    pr_data: Optional[Dict]
    analysis: Optional[str]
    comments: Optional[List[Dict[str, Any]]]
    review_summary: Optional[str]
    step: Optional[str]
    merge_decision: Optional[str]
    has_code_changes: Optional[bool]