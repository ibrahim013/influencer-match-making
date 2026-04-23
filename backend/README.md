# Influencer Matchmaking API

Python package and FastAPI service. Project overview and API docs live in the repository [README.md](../README.md).

## uv (recommended)

All dependency lock state is in this directory: **`pyproject.toml`** + **`uv.lock`**.

```bash
cd backend
uv sync --extra dev          # install runtime + dev (pytest, etc.)
uv run pytest tests -v
uv run uvicorn app.main:app --reload --app-dir .
```

Production / CI (no dev extras):

```bash
uv sync --frozen
```

After changing dependencies in `pyproject.toml`:

```bash
uv lock
uv sync --extra dev
```

Embeddings use **Pinecone Inference** (`llama-text-embed-v2` by default). Your index must match that model’s vector spec (see root README).

If you previously used another virtualenv at the repo root, either remove it or `unset VIRTUAL_ENV` so uv uses `backend/.venv` without warnings.
