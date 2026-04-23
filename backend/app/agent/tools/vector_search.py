from __future__ import annotations

import logging
from typing import Any

import httpx
from langchain_core.documents import Document
from langsmith import traceable
from openai import APIConnectionError, APITimeoutError, RateLimitError

from app.core.errors import ToolError, with_tool_retry

logger = logging.getLogger(__name__)

_PAGE_PREVIEW = 500


def _pinecone_hits_for_trace(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Smaller payload for LangSmith trace output (full rows still returned to the graph)."""
    out: list[dict[str, Any]] = []
    for r in rows:
        pc = str(r.get("page_content") or "")
        out.append(
            {
                "metadata": dict(r.get("metadata") or {}),
                "similarity_score": r.get("similarity_score"),
                "page_content_preview": pc[:_PAGE_PREVIEW],
            }
        )
    return out


def _pinecone_inputs_for_trace(inputs: dict[str, Any]) -> dict[str, Any]:
    bc = inputs.get("brand_context", "")
    if isinstance(bc, str) and len(bc) > 2000:
        bc = bc[:2000] + "…"
    return {
        "brand_context": bc,
        "k": inputs.get("k"),
        "index_name": inputs.get("index_name"),
    }


@traceable(
    run_type="retriever",
    name="pinecone_vector_search",
    process_inputs=_pinecone_inputs_for_trace,
    process_outputs=_pinecone_hits_for_trace,
)
async def run_pinecone_vector_search(
    *,
    brand_context: str,
    vector_store: Any,
    k: int,
    index_name: str,
) -> list[dict[str, Any]]:
    """Traced semantic search; outputs in LangSmith are previews via process_outputs."""
    try:
        pairs: list[tuple[Document, float]] = (
            await vector_store.asimilarity_search_with_score(brand_context, k=k)
        )
    except Exception as e:
        logger.exception("Pinecone vector search failed")
        raise ToolError(f"Pinecone search failed: {e}") from e

    out: list[dict[str, Any]] = []
    for doc, score in pairs:
        row: dict[str, Any] = {
            "page_content": doc.page_content,
            "metadata": dict(doc.metadata or {}),
            "similarity_score": float(score),
        }
        out.append(row)
    return out


class VectorSearchTool:
    """Semantic creator search backed by Pinecone (langchain-pinecone)."""

    def __init__(
        self,
        vector_store: Any,
        *,
        k: int = 12,
        index_name: str = "",
    ) -> None:
        self._vector_store = vector_store
        self._k = k
        self._index_name = index_name

    @with_tool_retry(
        max_attempts=3,
        exceptions=(
            APIConnectionError,
            APITimeoutError,
            RateLimitError,
            httpx.HTTPError,
            ConnectionError,
            TimeoutError,
        ),
    )
    async def search(self, brand_context: str) -> list[dict[str, Any]]:
        return await run_pinecone_vector_search(
            brand_context=brand_context,
            vector_store=self._vector_store,
            k=self._k,
            index_name=self._index_name or "unknown",
        )
