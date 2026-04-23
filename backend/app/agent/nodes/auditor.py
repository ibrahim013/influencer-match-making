from __future__ import annotations

import logging
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

from app.agent.context import AgentDeps
from app.agent.state import AgentState
from app.schemas.agent import AuditorResponse

logger = logging.getLogger(__name__)


def _get_deps(config: RunnableConfig) -> AgentDeps:
    deps = (config.get("configurable") or {}).get("deps")
    if deps is None:
        raise RuntimeError("RunnableConfig missing configurable['deps']")
    return deps


def _top_n(candidates: list[dict[str, Any]], n: int = 3) -> list[dict[str, Any]]:
    def score(c: dict[str, Any]) -> float:
        s = c.get("similarity_score")
        return float(s) if isinstance(s, (int, float)) else 0.0

    return sorted(candidates, key=score, reverse=True)[:n]


async def auditor_node(state: AgentState, config: RunnableConfig) -> dict[str, Any]:
    """Analyze top candidates for engagement quality and brand alignment (LLM + Pydantic)."""
    deps = _get_deps(config)
    logs = ["Auditor: evaluating top candidates for engagement quality…"]
    top = _top_n(state.get("candidate_list", []), 3)
    if not top:
        logs.append("Auditor: no candidates to audit.")
        return {"candidate_list": [], "logs": logs}

    structured = deps.llm.with_structured_output(AuditorResponse)
    sys = SystemMessage(
        content=(
            "You are an influencer fraud and quality analyst. "
            "Given a brand brief and up to three creator profiles, produce structured audits. "
            "Simulate signals for fake followers (inconsistent engagement vs followers, generic audience) "
            "and brand alignment. Output JSON matching the schema with at most one audit per creator."
        )
    )
    human = HumanMessage(
        content=(
            f"Brand brief:\n{state['brand_context']}\n\n"
            f"Creators (JSON):\n{top}"
        )
    )
    try:
        audits: AuditorResponse = await structured.ainvoke([sys, human])
    except Exception as e:
        logger.exception("Auditor LLM failed")
        logs.append(f"Auditor: LLM error ({e}); using conservative fallback audits.")
        audits = AuditorResponse(audits=[])

    by_id = {a.creator_id: a.model_dump() for a in audits.audits}
    enriched: list[dict[str, Any]] = []
    for c in top:
        cid = str(c.get("creator_id", ""))
        audit_blob = by_id.get(cid)
        if audit_blob is None:
            audit_blob = {
                "creator_id": cid,
                "engagement_quality_score": 5,
                "fake_follower_risk": "medium",
                "brand_alignment_notes": "No structured audit returned; manual review recommended.",
                "recommendation": "review_carefully",
            }
        row = {**c, "_engagement_audit": audit_blob}
        enriched.append(row)

    logs.append(
        f"Auditor: scored top {len(enriched)} creators; ready for human selection."
    )
    return {"candidate_list": enriched, "logs": logs}
