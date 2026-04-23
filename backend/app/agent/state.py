from __future__ import annotations

from operator import add
from typing import Annotated, NotRequired, TypedDict


class AgentState(TypedDict):
    """LangGraph agent state for influencer matchmaking."""

    brand_context: str
    candidate_list: list[dict]
    selected_candidate_id: str | None
    outreach_draft: str | None
    is_approved: bool
    logs: Annotated[list[str], add]
    # Extended fields for guardrail loop + routing
    refusal_reason: NotRequired[str | None]
    retry_count: NotRequired[int]
