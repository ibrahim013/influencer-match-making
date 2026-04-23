from __future__ import annotations

import json
import logging
from typing import Any

import anyio
from guardrails import Guard
from langchain_core.runnables import RunnableConfig

from app.agent.context import AgentDeps
from app.agent.state import AgentState
from app.core.errors import ToolError
from app.schemas.agent import OutreachDraft

logger = logging.getLogger(__name__)


def _get_deps(config: RunnableConfig) -> AgentDeps:
    deps = (config.get("configurable") or {}).get("deps")
    if deps is None:
        raise RuntimeError("RunnableConfig missing configurable['deps']")
    return deps


def _run_guarded_writer(
    deps: AgentDeps,
    *,
    brand_context: str,
    creator: dict[str, Any],
    refusal_reason: str | None,
) -> OutreachDraft:
    """Sync call executed in a worker thread (guardrails-ai + OpenAI sync client)."""
    guard: Guard = Guard.for_pydantic(OutreachDraft)
    prior = (
        f"\n\nRegenerate to fix guardrail feedback: {refusal_reason}"
        if refusal_reason
        else ""
    )
    system = (
        "You are an elite influencer partnerships ghostwriter. "
        "Write a concise, human outreach email. "
        "Reference exactly one concrete metadata fact from the creator JSON "
        "(e.g., a topic, geo, or engagement stat). "
        "Do not invent unavailable metrics. "
        "Never include bracket placeholders, ellipses placeholders, TODO, or competitor names."
        "Replece Your [name] placeholder with Management do not use [name] placeholder"
        + prior
    )
    user = f"Brand brief:\n{brand_context}\n\nCreator profile JSON:\n{creator}\n"
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]

    # Guardrails expects llm_api to return a raw string. OpenAI SDK v2 returns ChatCompletion.
    def _llm_api(*, messages: list[dict[str, Any]], model: str, **kwargs: Any) -> str:
        resp = deps.openai_sync.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs,
        )
        if not getattr(resp, "choices", None):
            raise ToolError("OpenAI returned no choices")
        content = resp.choices[0].message.content
        if not content:
            raise ToolError("OpenAI returned empty assistant content")
        return content

    def _call():
        outcome = guard(
            llm_api=_llm_api,
            model=deps.settings.openai_chat_model,
            messages=messages,
            num_reasks=1,
        )
        validated = outcome.validated_output
        if not outcome.validation_passed:
            raise ToolError(
                f"Guardrails validation failed: {outcome.error or outcome.validation_summaries}"
            )
        # Guardrails populates validated_output as JSON-shaped data (dict/str), not a model instance.
        if isinstance(validated, OutreachDraft):
            draft = validated
        elif isinstance(validated, dict):
            draft = OutreachDraft.model_validate(validated)
        elif isinstance(validated, str):
            draft = OutreachDraft.model_validate(json.loads(validated))
        else:
            raise ToolError(
                "Guardrails validated_output has unsupported type "
                f"({type(validated).__name__}); expected dict or OutreachDraft"
            )
        return draft

    return _call()


async def writer_node(state: AgentState, config: RunnableConfig) -> dict[str, Any]:
    """Draft outreach using guardrails-ai + GPT-4o (structured Pydantic output)."""
    deps = _get_deps(config)
    logs: list[str] = ["Writer: drafting personalized outreach (guardrails-ai + GPT-4o)…"]

    if not state.get("is_approved"):
        logs.append("Writer: is_approved is false — cannot draft yet.")
        return {"logs": logs}

    cid = state.get("selected_candidate_id")
    if not cid:
        logs.append("Writer: missing selected_candidate_id.")
        return {"logs": logs}

    selected = next(
        (c for c in state.get("candidate_list", []) if str(c.get("creator_id")) == str(cid)),
        None,
    )
    if selected is None:
        logs.append(f"Writer: selected id {cid} not found in candidate_list.")
        return {"logs": logs}

    refusal = state.get("refusal_reason")

    try:
        draft = await anyio.to_thread.run_sync(
            lambda: _run_guarded_writer(
                deps,
                brand_context=state["brand_context"],
                creator=selected,
                refusal_reason=refusal,
            ),
        )
    except Exception as e:
        logger.exception("Writer failed")
        logs.append(f"Writer: failed ({e})")
        raise ToolError(f"Writer failed: {e}") from e

    logs.append("Writer: outreach draft generated and schema-validated.")
    return {
        "outreach_draft": draft.model_dump_json(),
        "refusal_reason": None,
        "logs": logs,
    }
