from __future__ import annotations

import os

from app.config import Settings


def apply_langsmith_runtime_env(settings: Settings) -> None:
    """Sync process env with Settings so LangChain / LangGraph pick up tracing flags."""
    if settings.langsmith_tracing:
        os.environ["LANGSMITH_TRACING"] = "true"
        if settings.langsmith_api_key:
            os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key.strip()
        if settings.langsmith_project:
            os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project
        if settings.langsmith_workspace_id:
            os.environ["LANGSMITH_WORKSPACE_ID"] = settings.langsmith_workspace_id
    else:
        os.environ["LANGSMITH_TRACING"] = "false"
