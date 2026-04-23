from __future__ import annotations

import time
from typing import Any, cast
from uuid import UUID

import structlog
from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.outputs import LLMResult

from app.observability.llm_pricing import (
    estimate_llm_cost_usd,
    extract_token_usage,
    model_name_from_serialized,
)

GRAPH_NODE_NAMES = frozenset(
    {
        "researcher_node",
        "auditor_node",
        "human_review_node",
        "writer_node",
        "guardrail_validator",
    }
)

# Linear campaign DAG order (used to infer completed node before a resume).
DAG_NODE_ORDER = [
    "researcher_node",
    "auditor_node",
    "human_review_node",
    "writer_node",
    "guardrail_validator",
]


def infer_completed_before_next(next_nodes: list[str]) -> str | None:
    """Given LangGraph `snap.next`, return the node that logically finished before the next step."""
    if not next_nodes:
        return None
    n0 = next_nodes[0]
    if n0 not in GRAPH_NODE_NAMES:
        return None
    i = DAG_NODE_ORDER.index(n0)
    if i <= 0:
        return "__start__"
    return DAG_NODE_ORDER[i - 1]

log = structlog.get_logger("app.observability.langgraph")


def _graph_node_from_chain_event(
    serialized: dict[str, Any] | None,
    metadata: dict[str, Any] | None,
    kwargs: dict[str, Any],
) -> str | None:
    name = kwargs.get("name")
    if isinstance(name, str) and name in GRAPH_NODE_NAMES:
        return name
    if isinstance(serialized, dict):
        n = serialized.get("name")
        if isinstance(n, str) and n in GRAPH_NODE_NAMES:
            return n
    if metadata:
        n = metadata.get("langgraph_node")
        if isinstance(n, str) and n in GRAPH_NODE_NAMES:
            return n
    return None


class GraphObservabilityCallbackHandler(AsyncCallbackHandler):
    """Structured logs for LangGraph node boundaries, latency, and LLM token usage."""

    def __init__(
        self,
        *,
        thread_id: str,
        route: str,
        request_id: str | None,
        default_model: str,
        completed_before: str | None = None,
    ) -> None:
        super().__init__()
        self._thread_id = thread_id
        self._route = route
        self._request_id = request_id
        self._default_model = default_model
        self._last_completed_node: str | None = completed_before
        self._run_to_node: dict[UUID, str] = {}
        self._graph_root_run_ids: set[UUID] = set()
        self._chain_start_mono: dict[UUID, float] = {}
        self._llm_start_mono: dict[UUID, float] = {}
        self._last_llm_serialized: dict[UUID, dict[str, Any] | None] = {}

    def _base_kv(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "thread_id": self._thread_id,
            "route": self._route,
        }
        if self._request_id:
            out["request_id"] = self._request_id
        return out

    async def on_chain_start(
        self,
        serialized: dict[str, Any],
        inputs: dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        node = _graph_node_from_chain_event(serialized, metadata, kwargs)
        parent_node = self._run_to_node.get(parent_run_id) if parent_run_id else None
        if node:
            # LangGraph may emit a nested chain with the same `name` as the graph node;
            # skip duplicate roots so transitions stay one row per logical step.
            if (
                parent_run_id
                and parent_run_id in self._graph_root_run_ids
                and self._run_to_node.get(parent_run_id) == node
            ):
                self._run_to_node[run_id] = node
                return
            if parent_run_id and self._run_to_node.get(parent_run_id) == node:
                self._run_to_node[run_id] = node
                return

            self._run_to_node[run_id] = node
            self._graph_root_run_ids.add(run_id)
            self._chain_start_mono[run_id] = time.monotonic()
            log.info(
                "graph_transition",
                **self._base_kv(),
                from_node=self._last_completed_node or "__start__",
                to_node=node,
            )
            log.info(
                "graph_node_start",
                **self._base_kv(),
                node=node,
                run_id=str(run_id),
            )
        elif parent_node:
            self._run_to_node[run_id] = parent_node

    async def on_chain_end(
        self,
        outputs: Any,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        if run_id not in self._graph_root_run_ids:
            return
        node = self._run_to_node.get(run_id)
        t0 = self._chain_start_mono.pop(run_id, None)
        latency_ms = (
            round((time.monotonic() - t0) * 1000, 3) if t0 is not None else None
        )
        self._graph_root_run_ids.discard(run_id)
        if node:
            self._last_completed_node = node
        log.info(
            "graph_node_end",
            **self._base_kv(),
            node=node,
            run_id=str(run_id),
            latency_ms=latency_ms,
        )

    async def on_chain_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        if run_id in self._graph_root_run_ids:
            self._graph_root_run_ids.discard(run_id)
            self._chain_start_mono.pop(run_id, None)
            log.warning(
                "graph_node_error",
                **self._base_kv(),
                run_id=str(run_id),
                error_type=type(error).__name__,
                error=str(error),
            )

    async def on_llm_start(
        self,
        serialized: dict[str, Any],
        prompts: list[str],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        self._llm_start_mono[run_id] = time.monotonic()
        self._last_llm_serialized[run_id] = serialized

    async def on_chat_model_start(
        self,
        serialized: dict[str, Any],
        messages: list[list[Any]],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        self._llm_start_mono[run_id] = time.monotonic()
        self._last_llm_serialized[run_id] = serialized

    async def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        t0 = self._llm_start_mono.pop(run_id, None)
        latency_ms = (
            round((time.monotonic() - t0) * 1000, 3) if t0 is not None else None
        )
        ser = cast(
            dict[str, Any] | None, self._last_llm_serialized.pop(run_id, None)
        )

        node = "unknown"
        if parent_run_id is not None:
            node = self._run_to_node.get(parent_run_id, "unknown")

        usage = extract_token_usage(response)
        pt = usage["prompt_tokens"]
        ct = usage["completion_tokens"]
        tt = usage["total_tokens"]
        if tt is None and pt is not None and ct is not None:
            tt = pt + ct

        model = model_name_from_serialized(ser) or self._default_model

        est = None
        if pt is not None and ct is not None:
            est = estimate_llm_cost_usd(
                model=model, prompt_tokens=int(pt), completion_tokens=int(ct)
            )

        log.info(
            "llm_usage",
            **self._base_kv(),
            graph_node=node,
            model=model,
            prompt_tokens=pt,
            completion_tokens=ct,
            total_tokens=tt,
            latency_ms=latency_ms,
            estimated_usd=est,
            cost_note="estimated_usd is approximate list pricing for ops dashboards only",
        )
