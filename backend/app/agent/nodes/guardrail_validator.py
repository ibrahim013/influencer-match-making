from __future__ import annotations

import logging
from typing import Any

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END

from app.agent.context import AgentDeps
from app.agent.guardrails.competitor_check import find_competitor_mentions, find_placeholders
from app.agent.state import AgentState
from app.schemas.agent import GuardrailVerdict, OutreachDraft

logger = logging.getLogger(__name__)


def _get_deps(config: RunnableConfig) -> AgentDeps:
    deps = (config.get("configurable") or {}).get("deps")
    if deps is None:
        raise RuntimeError("RunnableConfig missing configurable['deps']")
    return deps


async def guardrail_validator_node(
    state: AgentState, config: RunnableConfig
) -> dict[str, Any]:
    """
    Outbound guardrails: competitor list, placeholders, and Pydantic integrity.
    On failure, sets refusal_reason and increments retry_count for the conditional edge.
    """
    deps = _get_deps(config)
    logs = ["GuardrailValidator: checking outbound draft…"]
    raw = state.get("outreach_draft")
    if not raw:
        reason = "Outreach draft missing before guardrail validation."
        logs.append(f"GuardrailValidator: FAIL — {reason}")
        return {
            "refusal_reason": reason,
            "retry_count": state.get("retry_count", 0) + 1,
            "logs": logs,
        }

    try:
        draft = OutreachDraft.model_validate_json(raw)
    except Exception as e:
        reason = f"Outreach draft is not valid OutreachDraft JSON: {e}"
        logs.append(f"GuardrailValidator: FAIL — {reason}")
        return {
            "refusal_reason": reason,
            "retry_count": state.get("retry_count", 0) + 1,
            "logs": logs,
        }

    combined = f"{draft.subject}\n{draft.body}\n{draft.cta}\n{draft.referenced_metadata}"
    issues: list[str] = []

    comps = find_competitor_mentions(combined, deps.settings.competitors)
    if comps:
        issues.append(f"competitor_mentions:{','.join(comps)}")

    ph = find_placeholders(combined)
    if ph:
        issues.append(f"placeholders:{','.join(ph[:5])}")

    passed = len(issues) == 0
    verdict = GuardrailVerdict(
        passed=passed,
        issues=issues,
        refusal_reason=None if passed else "; ".join(issues),
    )
    logs.append(f"GuardrailValidator: verdict={verdict.model_dump()}")

    if passed:
        return {"refusal_reason": None, "logs": logs}

    return {
        "refusal_reason": verdict.refusal_reason or "Outbound guardrail failure",
        "retry_count": state.get("retry_count", 0) + 1,
        "logs": logs,
    }


def route_after_guard(state: AgentState) -> str:
    """Route back to writer for limited retries, else end the run."""
    reason = state.get("refusal_reason")
    if reason:
        if state.get("retry_count", 0) < 3:
            return "writer_node"
        return END
    return END
