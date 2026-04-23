"""Embedding clients for vector search (Pinecone Inference by default)."""

from __future__ import annotations

from langchain_core.embeddings import Embeddings
from langchain_pinecone import PineconeEmbeddings
from pydantic import SecretStr

from app.config import Settings

# llama-text-embed-v2 default output size (see langchain_pinecone.embeddings defaults).
_TESTING_EMBED_DIM = 1024


class _TestingEmbeddings(Embeddings):
    """Deterministic vectors for unit tests; avoids Pinecone inference API at import/lifespan."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[0.0] * _TESTING_EMBED_DIM for _ in texts]

    def embed_query(self, text: str) -> list[float]:
        return [0.0] * _TESTING_EMBED_DIM


def make_embeddings(settings: Settings, *, testing: bool) -> Embeddings:
    if testing:
        return _TestingEmbeddings()
    return PineconeEmbeddings(
        model=settings.pinecone_embedding_model,
        pinecone_api_key=SecretStr(settings.pinecone_api_key),
    )
