from __future__ import annotations

import logging
from typing import Any

from langchain_core.runnables import RunnableConfig

from app.agent.context import AgentDeps
from app.agent.state import AgentState
from app.agent.tools.vector_search import VectorSearchTool
from app.schemas.agent import CandidateProfile

logger = logging.getLogger(__name__)


def _get_deps(config: RunnableConfig) -> AgentDeps:
    deps = (config.get("configurable") or {}).get("deps")
    if deps is None:
        raise RuntimeError("RunnableConfig missing configurable['deps']")
    return deps


async def researcher_node(state: AgentState, config: RunnableConfig) -> dict[str, Any]:
    """Query Pinecone for creators semantically similar to brand_context."""
    deps = _get_deps(config)
    tool = VectorSearchTool(
        deps.vector_store,
        index_name=deps.settings.pinecone_index_name,
    )
    logs: list[str] = ["Researcher: querying vector index for semantic matches…"]

    raw = await tool.search(state["brand_context"])
    candidates: list[dict[str, Any]] = []
    for row in raw:
        md = row.get("metadata") or {}
        try:
            profile = CandidateProfile(
                creator_id=str(md.get("creator_id", "")),
                handle=str(md.get("handle", "unknown")),
                niche=str(md.get("niche", "")),
                follower_count=int(md.get("follower_count", 0)),
                avg_engagement_rate=float(md.get("avg_engagement_rate", 0.0)),
                recent_post_topics=str(md.get("recent_post_topics", "")),
                audience_geo=str(md.get("audience_geo", "")),
                similarity_score=float(row["similarity_score"])
                if row.get("similarity_score") is not None
                else None,
            )
            if profile.creator_id:
                candidates.append(profile.model_dump())
        except Exception as e:
            logger.warning("Skipping malformed candidate metadata: %s", e)
            logs.append(f"Researcher: skipped malformed row ({e})")

    logs.append(f"Researcher: retrieved {len(candidates)} candidates from Pinecone.")
    return {"candidate_list": candidates, "logs": logs}
