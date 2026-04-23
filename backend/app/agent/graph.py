from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from app.agent.nodes.auditor import auditor_node
from app.agent.nodes.guardrail_validator import (
    guardrail_validator_node,
    route_after_guard,
)
from app.agent.nodes.human_review import human_review_node
from app.agent.nodes.researcher import researcher_node
from app.agent.nodes.writer import writer_node
from app.agent.state import AgentState


def build_campaign_graph() -> StateGraph:
    """DAG: researcher → auditor → human_review → writer → guardrail_validator (+ conditional retry)."""
    g = StateGraph(AgentState)
    g.add_node("researcher_node", researcher_node)
    g.add_node("auditor_node", auditor_node)
    g.add_node("human_review_node", human_review_node)
    g.add_node("writer_node", writer_node)
    g.add_node("guardrail_validator", guardrail_validator_node)

    g.add_edge(START, "researcher_node")
    g.add_edge("researcher_node", "auditor_node")
    g.add_edge("auditor_node", "human_review_node")
    g.add_edge("human_review_node", "writer_node")
    g.add_edge("writer_node", "guardrail_validator")
    g.add_conditional_edges(
        "guardrail_validator",
        route_after_guard,
        {"writer_node": "writer_node", END: END},
    )
    return g
