from __future__ import annotations

import logging
from typing import Any

from langchain_core.runnables import RunnableConfig

from app.agent.state import AgentState

logger = logging.getLogger(__name__)


async def human_review_node(state: AgentState, config: RunnableConfig) -> dict[str, Any]:
    """
    Virtual HITL checkpoint node.
    Execution pauses before writer_node via interrupt_before on the compiled graph.
    """
    n = len(state.get("candidate_list", []))
    ids = [str(c.get("creator_id")) for c in state.get("candidate_list", [])]
    logs = [
        "HumanReview: shortlist ready for UI approval.",
        f"HumanReview: {n} candidate(s) in state; ids={ids}.",
        "HumanReview: awaiting POST /campaign/{thread_id}/approve to set selection and resume.",
    ]
    logger.info("human_review_node thread=%s", (config.get("configurable") or {}).get("thread_id"))
    return {"logs": logs}
