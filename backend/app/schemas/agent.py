from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class CandidateProfile(BaseModel):
    """Structured representation of a creator returned from vector search."""

    creator_id: str = Field(description="Stable creator identifier")
    handle: str
    niche: str
    follower_count: int = Field(ge=0)
    avg_engagement_rate: float = Field(ge=0, le=1, description="0–1 fraction")
    recent_post_topics: str = Field(description="Comma-separated or short summary")
    audience_geo: str
    similarity_score: float | None = Field(
        default=None, description="Vector similarity if available"
    )


class EngagementAudit(BaseModel):
    """Auditor assessment for one creator (top-3 review)."""

    creator_id: str
    engagement_quality_score: int = Field(ge=1, le=10)
    fake_follower_risk: Literal["low", "medium", "high"]
    brand_alignment_notes: str
    recommendation: Literal["proceed", "review_carefully", "exclude"]


class AuditorResponse(BaseModel):
    """LLM structured output for the auditor node."""

    audits: list[EngagementAudit] = Field(
        default_factory=list,
        description="Up to three audits for the top candidates",
    )


class OutreachDraft(BaseModel):
    """Ghostwriter structured pitch — validated by guardrails-ai + Pydantic."""

    subject: str = Field(max_length=200)
    body: str = Field(description="Email-style outreach body")
    cta: str = Field(description="Single clear call-to-action")
    referenced_metadata: str = Field(
        description="One concrete metadata point cited from the creator profile"
    )


class GuardrailVerdict(BaseModel):
    """Outbound guardrail result — parsed, not raw strings."""

    passed: bool
    issues: list[str] = Field(default_factory=list)
    refusal_reason: str | None = None
