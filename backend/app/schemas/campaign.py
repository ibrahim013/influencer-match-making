from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class StartCampaignRequest(BaseModel):
    brand_context: str = Field(
        min_length=10,
        max_length=8000,
        description="Brand brief used for semantic creator matching",
    )


class StartCampaignResponse(BaseModel):
    thread_id: str


class ApproveCampaignRequest(BaseModel):
    selected_candidate_id: str = Field(
        description="creator_id chosen from the audited shortlist"
    )


class ApproveCampaignResponse(BaseModel):
    status: Literal["resumed"]


class StreamEvent(BaseModel):
    """SSE payload for graph updates."""

    type: Literal["graph_update", "state_snapshot", "error", "done"]
    thread_id: str | None = None
    node: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
