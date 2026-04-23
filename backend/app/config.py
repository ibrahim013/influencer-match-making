from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    openai_chat_model: str = Field(default="gpt-4o", alias="OPENAI_CHAT_MODEL")

    pinecone_api_key: str = Field(..., alias="PINECONE_API_KEY")
    pinecone_embedding_model: str = Field(
        default="llama-text-embed-v2",
        alias="PINECONE_EMBEDDING_MODEL",
        description="Pinecone Inference embedding model (see Pinecone docs / langchain_pinecone.PineconeEmbeddings).",
    )
    pinecone_index_name: str = Field(
        default="influencer-creators", alias="PINECONE_INDEX_NAME"
    )
    pinecone_environment: str | None = Field(default=None, alias="PINECONE_ENVIRONMENT")

    database_url: str = Field(..., alias="DATABASE_URL")

    competitor_list: str = Field(
        default="Nike,Adidas,Puma",
        alias="COMPETITOR_LIST",
        description="Comma-separated competitor brand names for outbound guardrails.",
    )

    guardrails_run_sync: bool = Field(
        default=True,
        alias="GUARDRAILS_RUN_SYNC",
        description=(
            "Use Guardrails synchronous validators (recommended with FastAPI / "
            "thread pools). Set false only if validators run on the main asyncio thread."
        ),
    )

    log_format: Literal["text", "json"] = Field(
        default="text",
        alias="LOG_FORMAT",
        description="Structured logs: json for log drains; text for local dev.",
    )

    langsmith_tracing: bool = Field(
        default=False,
        alias="LANGSMITH_TRACING",
        description="Send LangGraph/LangChain traces to LangSmith.",
    )
    langsmith_api_key: str | None = Field(default=None, alias="LANGSMITH_API_KEY")
    langsmith_project: str | None = Field(default=None, alias="LANGSMITH_PROJECT")
    langsmith_workspace_id: str | None = Field(
        default=None, alias="LANGSMITH_WORKSPACE_ID"
    )

    @model_validator(mode="after")
    def _langsmith_requires_key(self) -> "Settings":
        if self.langsmith_tracing and not (self.langsmith_api_key or "").strip():
            raise ValueError("LANGSMITH_TRACING is true but LANGSMITH_API_KEY is missing")
        return self

    @property
    def competitors(self) -> list[str]:
        return [c.strip() for c in self.competitor_list.split(",") if c.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


def clear_settings_cache() -> None:
    get_settings.cache_clear()
