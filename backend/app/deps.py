"""
FastAPI dependency injection helpers (graph + agent runtime objects on `app.state`).
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import Request

from app.agent.context import AgentDeps


def get_graph(request: Request) -> Any:
    return request.app.state.graph


def get_agent_deps(request: Request) -> AgentDeps:
    return request.app.state.agent_deps


GraphDep = Annotated[Any, get_graph]
AgentDepsDep = Annotated[AgentDeps, get_agent_deps]
