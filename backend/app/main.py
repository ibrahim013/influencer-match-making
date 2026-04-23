from __future__ import annotations

import logging
import os
import uuid
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langsmith.wrappers import wrap_openai
from starlette.requests import Request
from starlette.responses import Response
from langchain_core.embeddings import Embeddings
from langchain_openai import ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from openai import AsyncOpenAI, OpenAI
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from app.agent.context import AgentDeps
from app.agent.graph import build_campaign_graph
from app.api.campaigns import router as campaigns_router
from app.config import get_settings
from app.embeddings import make_embeddings
from app.core.logging import configure_logging
from app.observability.langsmith_env import apply_langsmith_runtime_env

logger = logging.getLogger(__name__)


def _vector_store(settings: Any, embeddings: Embeddings) -> PineconeVectorStore:
    return PineconeVectorStore.from_existing_index(
        index_name=settings.pinecone_index_name,
        embedding=embeddings,
        text_key="text",
    )


class _NoOpVectorStore:
    """Placeholder when TESTING=1 so lifespan never calls Pinecone with dummy API keys."""

    async def asimilarity_search_with_score(
        self, *args: Any, **kwargs: Any
    ) -> list[tuple[Any, float]]:
        return []


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(log_format=settings.log_format)
    apply_langsmith_runtime_env(settings)
    # Guardrails reads GUARDRAILS_RUN_SYNC at validate time; sync mode avoids
    # "Could not obtain an event loop" when guard runs in a worker thread.
    os.environ["GUARDRAILS_RUN_SYNC"] = (
        "true" if settings.guardrails_run_sync else "false"
    )
    testing = os.getenv("TESTING", "").lower() in ("1", "true", "yes")

    embeddings = make_embeddings(settings, testing=testing)
    llm = ChatOpenAI(
        model=settings.openai_chat_model,
        api_key=settings.openai_api_key,
        temperature=0.2,
    )
    if testing:
        vector_store = _NoOpVectorStore()  # type: ignore[assignment]
    else:
        vector_store = _vector_store(settings, embeddings)
    oa_async = AsyncOpenAI(api_key=settings.openai_api_key)
    oa_sync = OpenAI(api_key=settings.openai_api_key)
    if settings.langsmith_tracing:
        oa_async = wrap_openai(oa_async)
        oa_sync = wrap_openai(oa_sync)
    app.state.agent_deps = AgentDeps(
        settings=settings,
        llm=llm,
        embeddings=embeddings,
        vector_store=vector_store,
        openai_client=oa_async,
        openai_sync=oa_sync,
    )
    app.state.background_tasks = set()

    if testing:
        app.state.pool = None
        checkpointer: Any = MemorySaver()
        logger.warning("TESTING mode: using MemorySaver checkpointer")
    else:
        pool = AsyncConnectionPool(
            conninfo=settings.database_url,
            kwargs={"autocommit": True, "prepare_threshold": 0, "row_factory": dict_row},
            open=False,
        )
        await pool.open()
        app.state.pool = pool
        checkpointer = AsyncPostgresSaver(pool)
        await checkpointer.setup()

    graph = build_campaign_graph().compile(
        checkpointer=checkpointer,
        interrupt_before=["writer_node"],
    )
    app.state.graph = graph
    logger.info("LangGraph compiled with interrupt_before=['writer_node']")
    yield
    if getattr(app.state, "pool", None) is not None:
        await app.state.pool.close()


app = FastAPI(title="Influencer Matchmaking Engine", lifespan=lifespan)

_cors_origins = [
    o.strip()
    for o in os.getenv(
        "CORS_ALLOW_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if o.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next: Any) -> Response:
    rid = request.headers.get("x-request-id") or str(uuid.uuid4())
    request.state.request_id = rid
    response = await call_next(request)
    response.headers["X-Request-ID"] = rid
    return response


app.include_router(campaigns_router, prefix="/campaign", tags=["campaign"])


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}
