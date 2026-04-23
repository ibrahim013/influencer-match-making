from __future__ import annotations

import os

import pytest

# Configure env before importing the FastAPI app (settings + lifespan).
os.environ.setdefault("TESTING", "1")
os.environ.setdefault("OPENAI_API_KEY", "sk-test-key")
os.environ.setdefault("PINECONE_API_KEY", "pc-test-key")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://langgraph:langgraph@localhost:5432/langgraph",
)
os.environ.setdefault("PINECONE_INDEX_NAME", "influencer-creators")
os.environ.setdefault("COMPETITOR_LIST", "Nike,Adidas")


@pytest.fixture()
def anyio_backend() -> str:
    return "asyncio"
