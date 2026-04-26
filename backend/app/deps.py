"""
FastAPI dependency injection helpers (graph + agent runtime objects on `app.state`).
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import HTTPException, Request

from app.agent.context import AgentDeps


def get_graph(request: Request) -> Any:
    if not getattr(request.app.state, "api_ready", False):
        raise HTTPException(status_code=503, detail="API is still starting")
    return request.app.state.graph


def get_agent_deps(request: Request) -> AgentDeps:
    if not getattr(request.app.state, "api_ready", False):
        raise HTTPException(status_code=503, detail="API is still starting")
    return request.app.state.agent_deps


GraphDep = Annotated[Any, get_graph]
AgentDepsDep = Annotated[AgentDeps, get_agent_deps]
