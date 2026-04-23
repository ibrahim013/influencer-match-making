from __future__ import annotations

from typing import Any
import asyncio
import time

import pytest
from langgraph.graph import END
from starlette.testclient import TestClient

from app.agent.nodes.guardrail_validator import route_after_guard
from app.config import clear_settings_cache
from app.main import app
from app.schemas.agent import AuditorResponse, EngagementAudit, OutreachDraft


class _FakeVS:
    async def asimilarity_search_with_score(
        self, query: str, k: int = 10, **kwargs: Any
    ) -> list[tuple[Any, float]]:
        from langchain_core.documents import Document

        docs = [
            Document(
                page_content="wellness creator focused on hydration",
                metadata={
                    "creator_id": "cr_001",
                    "handle": "@wellness_ava",
                    "niche": "wellness",
                    "follower_count": 120_000,
                    "avg_engagement_rate": 0.04,
                    "recent_post_topics": "hydration,electrolytes",
                    "audience_geo": "US",
                },
            ),
            Document(
                page_content="food creator for busy parents",
                metadata={
                    "creator_id": "cr_002",
                    "handle": "@snack_parent",
                    "niche": "food",
                    "follower_count": 80_000,
                    "avg_engagement_rate": 0.055,
                    "recent_post_topics": "snacks,meal prep",
                    "audience_geo": "US",
                },
            ),
            Document(
                page_content="running coach and shoe reviewer",
                metadata={
                    "creator_id": "cr_003",
                    "handle": "@runwithmia",
                    "niche": "running",
                    "follower_count": 200_000,
                    "avg_engagement_rate": 0.03,
                    "recent_post_topics": "marathon,recovery",
                    "audience_geo": "UK",
                },
            ),
        ]
        return [(d, 0.9 - i * 0.1) for i, d in enumerate(docs[:k])]


class _FakeStructuredAuditor:
    async def ainvoke(self, messages: Any) -> AuditorResponse:
        return AuditorResponse(
            audits=[
                EngagementAudit(
                    creator_id="cr_001",
                    engagement_quality_score=8,
                    fake_follower_risk="low",
                    brand_alignment_notes="Strong match for hydration products.",
                    recommendation="proceed",
                ),
                EngagementAudit(
                    creator_id="cr_002",
                    engagement_quality_score=7,
                    fake_follower_risk="low",
                    brand_alignment_notes="Good for family snack positioning.",
                    recommendation="proceed",
                ),
                EngagementAudit(
                    creator_id="cr_003",
                    engagement_quality_score=6,
                    fake_follower_risk="medium",
                    brand_alignment_notes="Endurance audience overlap.",
                    recommendation="review_carefully",
                ),
            ]
        )


class _FakeLLM:
    def with_structured_output(self, model: Any) -> _FakeStructuredAuditor:
        return _FakeStructuredAuditor()


@pytest.fixture(autouse=True)
def _clear_settings() -> Any:
    clear_settings_cache()
    yield
    clear_settings_cache()


def test_interrupt_before_writer_then_approve(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TESTING", "1")
    clear_settings_cache()

    async def _fake_validate_input(text: str, oa: Any) -> None:
        return None

    monkeypatch.setattr("app.api.campaigns.validate_input", _fake_validate_input)

    def _fake_writer(*args: Any, **kwargs: Any) -> OutreachDraft:
        return OutreachDraft(
            subject="Partnership idea",
            body="Loved your electrolytes series — perfect fit for our hydration mix.",
            cta="Open to a 60s integration this month?",
            referenced_metadata="recent_post_topics: hydration,electrolytes",
        )

    monkeypatch.setattr("app.agent.nodes.writer._run_guarded_writer", _fake_writer)

    with TestClient(app) as client:
        app_obj = client.app
        app_obj.state.agent_deps.vector_store = _FakeVS()
        app_obj.state.agent_deps.llm = _FakeLLM()

        r = client.post(
            "/campaign/start",
            json={"brand_context": "We sell premium hydration mixes for active parents in the US."},
        )
        assert r.status_code == 200, r.text
        thread_id = r.json()["thread_id"]

        async def _snap() -> Any:
            return await app_obj.state.graph.aget_state(
                {"configurable": {"thread_id": thread_id, "deps": app_obj.state.agent_deps}}
            )

        snap = asyncio.run(_snap())
        assert "writer_node" in snap.next
        assert snap.values.get("is_approved") is False

        apr = client.post(
            f"/campaign/{thread_id}/approve",
            json={"selected_candidate_id": "cr_001"},
        )
        assert apr.status_code == 200, apr.text

        for _ in range(50):
            time.sleep(0.1)
            snap = asyncio.run(_snap())
            if not snap.next and snap.values.get("outreach_draft"):
                break

        assert snap.values.get("outreach_draft")
        raw = snap.values["outreach_draft"]
        assert "hydration" in raw.lower() or "electrolytes" in raw.lower()


def test_route_guard_edges() -> None:
    s_fail = {
        "brand_context": "x",
        "candidate_list": [],
        "selected_candidate_id": None,
        "outreach_draft": None,
        "is_approved": True,
        "logs": [],
        "refusal_reason": "competitor_mentions:Nike",
        "retry_count": 3,
    }
    assert route_after_guard(s_fail) == END

    s_retry = {
        "brand_context": "x",
        "candidate_list": [],
        "selected_candidate_id": None,
        "outreach_draft": None,
        "is_approved": True,
        "logs": [],
        "refusal_reason": "placeholders:...",
        "retry_count": 1,
    }
    assert route_after_guard(s_retry) == "writer_node"

    s_ok = {
        "brand_context": "x",
        "candidate_list": [],
        "selected_candidate_id": None,
        "outreach_draft": "{}",
        "is_approved": True,
        "logs": [],
        "refusal_reason": None,
        "retry_count": 2,
    }
    assert route_after_guard(s_ok) == END
