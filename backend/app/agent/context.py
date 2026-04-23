from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from langchain_core.embeddings import Embeddings
from langchain_openai import ChatOpenAI
from openai import AsyncOpenAI, OpenAI

from app.config import Settings


@runtime_checkable
class VectorStoreLike(Protocol):
    async def asimilarity_search_with_score(
        self, query: str, k: int = 4, **kwargs: Any
    ) -> list[tuple[Any, float]]: ...


@dataclass(slots=True)
class AgentDeps:
    """Injected into LangGraph via RunnableConfig['configurable']['deps']."""

    settings: Settings
    llm: ChatOpenAI
    embeddings: Embeddings
    vector_store: VectorStoreLike
    openai_client: AsyncOpenAI
    openai_sync: OpenAI
