from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.agent.context import AgentDeps
from app.agent.state import AgentState
from app.agent.tools.moderation import validate_input
from app.core.errors import ToolError
from app.deps import get_agent_deps, get_graph
from app.observability.langchain_callbacks import (
    GraphObservabilityCallbackHandler,
    infer_completed_before_next,
)
from app.schemas.campaign import (
    ApproveCampaignRequest,
    ApproveCampaignResponse,
    StartCampaignRequest,
    StartCampaignResponse,
)

logger = logging.getLogger(__name__)

# ALB / proxies idle out long-poll SSE if no bytes are sent (graph paused at HITL).
_SSE_KEEPALIVE_INTERVAL_SEC = 15.0

router = APIRouter()


def _sse_payload(obj: dict[str, Any]) -> str:
    return f"data: {json.dumps(obj, default=str)}\n\n"


def _thread_config(deps: AgentDeps, thread_id: str) -> dict[str, Any]:
    """Minimal config for reads (e.g. aget_state) that do not need observability callbacks."""
    return {"configurable": {"thread_id": thread_id, "deps": deps}}


def graph_invoke_config(
    deps: AgentDeps,
    thread_id: str,
    *,
    route: Literal["start", "resume"],
    request_id: str | None,
    completed_before: str | None = None,
) -> dict[str, Any]:
    """RunnableConfig for graph.ainvoke with LangSmith metadata and structured-log callbacks."""
    obs = GraphObservabilityCallbackHandler(
        thread_id=thread_id,
        route=route,
        request_id=request_id,
        default_model=deps.settings.openai_chat_model,
        completed_before=completed_before,
    )
    meta: dict[str, Any] = {
        "thread_id": thread_id,
        "route": route,
    }
    if request_id:
        meta["request_id"] = request_id
    return {
        "configurable": {"thread_id": thread_id, "deps": deps},
        "metadata": meta,
        "tags": ["app:matchmaking", f"route:{route}"],
        "callbacks": [obs],
    }


def _assert_thread_ready(snap: Any) -> None:
    vals = snap.values if isinstance(snap.values, dict) else {}
    if not vals or not vals.get("brand_context"):
        raise HTTPException(status_code=404, detail="Unknown or uninitialized thread_id")


@router.post("/start", response_model=StartCampaignResponse)
async def start_campaign(
    request: Request,
    body: StartCampaignRequest,
    graph: Annotated[Any, Depends(get_graph)],
    deps: Annotated[AgentDeps, Depends(get_agent_deps)],
) -> StartCampaignResponse:
    try:
        await validate_input(body.brand_context, deps.openai_client)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except ToolError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e

    thread_id = str(uuid.uuid4())
    rid = getattr(request.state, "request_id", None)
    config = graph_invoke_config(
        deps, thread_id, route="start", request_id=rid if isinstance(rid, str) else None
    )
    initial: AgentState = {
        "brand_context": body.brand_context,
        "candidate_list": [],
        "selected_candidate_id": None,
        "outreach_draft": None,
        "is_approved": False,
        "logs": ["Campaign: graph run started."],
        "refusal_reason": None,
        "retry_count": 0,
    }
    try:
        await graph.ainvoke(initial, config)
    except Exception as e:
        logger.exception("Campaign start failed")
        raise HTTPException(status_code=500, detail=f"Graph execution failed: {e}") from e

    return StartCampaignResponse(thread_id=thread_id)


async def _resume_graph(graph: Any, config: dict[str, Any]) -> None:
    try:
        await graph.ainvoke(None, config)
    except Exception:
        logger.exception("Background graph resume failed")


@router.post("/{thread_id}/approve", response_model=ApproveCampaignResponse)
async def approve_campaign(
    thread_id: str,
    body: ApproveCampaignRequest,
    request: Request,
    graph: Annotated[Any, Depends(get_graph)],
    deps: Annotated[AgentDeps, Depends(get_agent_deps)],
) -> ApproveCampaignResponse:
    snap = await graph.aget_state(_thread_config(deps, thread_id))
    _assert_thread_ready(snap)
    rid = getattr(request.state, "request_id", None)
    completed_before = infer_completed_before_next(list(snap.next))
    config = graph_invoke_config(
        deps,
        thread_id,
        route="resume",
        request_id=rid if isinstance(rid, str) else None,
        completed_before=completed_before,
    )
    vals = snap.values
    shortlist = {str(c.get("creator_id")) for c in vals.get("candidate_list", [])}
    if body.selected_candidate_id not in shortlist:
        raise HTTPException(
            status_code=400,
            detail="selected_candidate_id must be one of the shortlisted creator_id values",
        )

    await graph.aupdate_state(
        _thread_config(deps, thread_id),
        {
            "is_approved": True,
            "selected_candidate_id": body.selected_candidate_id,
        },
    )
    task = asyncio.create_task(_resume_graph(graph, config))
    request.app.state.background_tasks.add(task)
    task.add_done_callback(request.app.state.background_tasks.discard)
    return ApproveCampaignResponse(status="resumed")


@router.get("/{thread_id}/stream")
async def stream_campaign(
    thread_id: str,
    request: Request,
    graph: Annotated[Any, Depends(get_graph)],
    deps: Annotated[AgentDeps, Depends(get_agent_deps)],
) -> StreamingResponse:
    """
    Server-Sent Events stream of graph state snapshots (polling-based).
    This avoids calling graph.astream/ainvoke from the reader, which would prematurely
    resume execution before human approval.
    """
    config = _thread_config(deps, thread_id)

    async def event_generator() -> Any:
        snap = await graph.aget_state(config)
        try:
            _assert_thread_ready(snap)
        except HTTPException as e:
            yield _sse_payload({"type": "error", "detail": e.detail})
            return

        last: str | None = None
        last_sent = time.monotonic()
        try:
            while True:
                if await request.is_disconnected():
                    break
                snap = await graph.aget_state(config)
                vals = snap.values if isinstance(snap.values, dict) else {}
                payload = {
                    "type": "state_snapshot",
                    "thread_id": thread_id,
                    "next": list(snap.next),
                    "values": vals,
                }
                fingerprint = json.dumps(payload, default=str, sort_keys=True)
                if fingerprint != last:
                    last = fingerprint
                    yield _sse_payload(payload)
                    last_sent = time.monotonic()
                if not snap.next:
                    yield _sse_payload({"type": "done", "thread_id": thread_id})
                    break
                await asyncio.sleep(0.35)
                if time.monotonic() - last_sent >= _SSE_KEEPALIVE_INTERVAL_SEC:
                    yield ": keep-alive\n\n"
                    last_sent = time.monotonic()
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.exception("SSE stream failed")
            yield _sse_payload({"type": "error", "detail": str(e)})

    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }
    return StreamingResponse(event_generator(), media_type="text/event-stream", headers=headers)
