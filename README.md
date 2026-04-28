# Influencer Matchmaking Engine

> **Find & shortlist creators for campaigns using an agentic, vector-backed pipeline, HITL review, and real-time dashboard.**

---

![Architecture Diagram](docs/architecture.png) <!-- Optional: Replace with your diagram -->

## Features

- **Automatic Matching:** Finds and recommends creators based on campaign brief.
- **Human-in-the-Loop:** Approvals and interventions at key pipeline stages.
- **Real-time Dashboard:** View agent/campaign status, review candidates, and approve selections instantly.
- **Streamed Updates:** SSE/WebSocket for low-latency UI sync.
- **Modern stack:** FastAPI, React (Vite+TS), Pinecone, OpenAI, Tailwind, Terraform, GitHub Actions.

---

## Table of Contents

- [About](#about)
- [Features](#features)
- [Architecture Overview](#architecture-overview)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
    - [Docker](#docker)
    - [Local Development](#local-development)
    - [Frontend](#frontend)
- [Deployment](#deployment)
    - [AWS (Terraform + GitHub Actions)](#aws-terraform--github-actions)
- [API Overview](#api-overview)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)
- [Project Layout](#project-layout)
- [Contributing](#contributing)

---

## About

Influencer Matchmaking helps brands find and shortlist creators who best fit a given campaign brief. An agentic pipeline researches candidates from a vector-based index, applies moderation and filtering, and lets you approve or reject recommendations directly in a modern dashboard.

---

## Architecture Overview

- **Backend:**  
  Orchestrates the agentic workflow via a LangGraph graph of nodes:
    - `researcher_node` → `auditor_node` → `human_review_node` → *(interrupt before `writer_node`)* → `writer_node` → `guardrail_validator`
    - Interrupts at human-review; resumes via approval endpoint and completes pipeline.
  - Exposes API via FastAPI.
  - Streams real-time state updates using SSE.
  - Uses Pinecone for search/indexing and OpenAI for intelligence.

- **Frontend:**  
  Monorepo with `frontend/` as a Vite+TypeScript app featuring:
    - React Query for state management and API sync.
    - Realtime UI updates from backend streams (WebSocket/SSE).
    - Tailwind, shadcn/ui, Lucide icons for modern DX.

- **AWS Cloud:**  
  - API deployed to AWS App Runner.
  - Frontend static on S3 + CloudFront.
  - IaC via Terraform; deployment managed with GitHub Actions.

---

## Tech Stack

| Layer      | Main Tools / Libraries                                                    |
|------------|--------------------------------------------------------------------------|
| Backend    | FastAPI, LangGraph, Pinecone (via langchain-pinecone), OpenAI, Pydantic v2, guardrails-ai, Postgres |
| Frontend   | React (Vite), TypeScript, Tailwind CSS, shadcn/ui, Lucide, React Query, Framer Motion |
| DevOps     | Docker, Terraform, GitHub Actions, AWS (App Runner, S3, CloudFront, RDS), uv+pytest |

---

## Quick Start

### Docker

1. **Copy and configure environment:**

    ```bash
    cp backend/.env.example backend/.env
    # Edit backend/.env to set OPENAI_API_KEY, PINECONE_API_KEY, and the Pinecone index name
    ```

2. **Build and run services:**

    ```bash
    docker compose up --build
    # API: http://localhost:8000/docs
    ```

3. **Seed Pinecone (host networking):**

    ```bash
    docker compose run --rm -e OPENAI_API_KEY -e PINECONE_API_KEY backend \
      python scripts/seed_pinecone.py
    ```

---

### Local Development

**Backend (with uv):**
```bash
cd backend
uv sync --extra dev
export DATABASE_URL=postgresql://langgraph:langgraph@localhost:5432/langgraph
export OPENAI_API_KEY=...
export PINECONE_API_KEY=...
unset TESTING   # Use real Postgres checkpointer
uv run uvicorn app.main:app --reload --app-dir .
```

**Tests (uses in-memory fakes, no Pinecone/OpenAI):**
```bash
cd backend
uv run pytest tests -v
```

Update lockfile after changing dependencies:
```bash
cd backend && uv lock
```

---

### Frontend

1. Ensure backend API is running/available at the correct URL.
2. In a new shell:
    ```bash
    cd frontend
    npm install
    npm run dev
    ```
3. Open [http://localhost:5173](http://localhost:5173).  
   (Configure API base URL with `frontend/.env` and `VITE_API_BASE_URL` if using non-default backend.)

---

## Deployment

### AWS (Terraform + GitHub Actions)

- **Infra:** S3 (static), CloudFront, App Runner, RDS, VPC via Terraform in `infra/`.
- **One-time:**
    - Run Terraform in [`infra/bootstrap/`](infra/bootstrap/) to create remote state and lock.
    - Copy/adjust `infra/envs/dev/backend.hcl.example` for your dev stack.

- **Credentials:**  
  Set repo variables: `AWS_REGION`, `AWS_DEPLOY_ROLE_ARN`, `TF_STATE_BUCKET`, `TF_LOCK_TABLE`.  
  Secrets: `OPENAI_API_KEY`, `PINECONE_API_KEY`.  
  Optional: `LANGSMITH_API_KEY`, `PINECONE_INDEX_NAME`, `COMPETITOR_LIST`.

- **Workflows:**  
  Push to `main` auto-deploys via [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml).  
  Destroy with [`.github/workflows/destroy.yml`](.github/workflows/destroy.yml) (manual: type `DESTROY` to confirm).

**App Runner will stop taking new customers after April 2026; consider alternatives for future apps.**

---

## API Overview

- `POST /campaign/start`  
  Start a campaign with `brand_context`. Moderation runs, then graph executes to review stage.
  ```json
  { "brand_context": "We are an organic snack brand targeting US parents…" }
  ```

- `GET /campaign/{thread_id}/stream`  
  Stream state frames:
  - `{"type":"state_snapshot", ...}`
  - `{"type":"done", ...}`

- `POST /campaign/{thread_id}/approve`  
  Select candidate; resumes pipeline.  
  ```json
  { "selected_candidate_id": "cr_001" }
  ```

See [`backend/app/api/campaigns.py`](backend/app/api/campaigns.py) for full details.

---

## Environment Variables

See [`backend/.env.example`](backend/.env.example) for all options.

| Variable                | Example                            | Description |
|-------------------------|------------------------------------|-------------|
| `OPENAI_API_KEY`        | (string)                           | OpenAI API key (required) |
| `PINECONE_API_KEY`      | (string)                           | Pinecone API key (required) |
| `PINECONE_EMBEDDING_MODEL` | llama-text-embed-v2             | Pinecone embedding model (default: `llama-text-embed-v2`) |
| `COMPETITOR_LIST`       | Adidas,Nike,Puma                   | Comma-separated competitor names (optional) |
| `DATABASE_URL`          | postgres://...                     | Postgres connection string |
| ...                     | ...                                | See `.env.example` for full list  |

---

## Troubleshooting

- **Docker fails to start:** Check `.env` files and required keys, then rebuild (`docker compose build --no-cache`).
- **Pinecone errors:** Make sure your API key and index model match your Pinecone project.
- **Frontend can't connect to API:** Verify `VITE_API_BASE_URL` and backend is running.
- **App Runner timeouts:** Service may be paused or have hit the 120s request cap; see AWS docs for limits.

---

## Project Layout

- `backend/app` — FastAPI app, LangGraph graph, nodes, schemas
- `backend/scripts/seed_pinecone.py` — Seed demo creators
- `frontend/` — React + Vite app
- `infra/` — Terraform IaC (see `infra/README.md`)
- `docker-compose.yaml` — Postgres + API services

---

## Contributing

Contributions welcome! Please:
- Open issues for bugs or feature requests
- Submit pull requests for improvements or fixes
- See [CONTRIBUTING.md](CONTRIBUTING.md) (if available) for coding guidelines

---

**[⬆ Back to top](#influencer-matchmaking-engine)**
