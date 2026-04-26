# Influencer Matchmaking Engine

## About

Influencer Matchmaking helps brands find and shortlist creators who fit a campaign brief. You describe the brand and goals; an agentic pipeline researches candidates from a vector-backed creator index, audits fit, and surfaces a ranked list for human-in-the-loop review. After you approve a creator, the system drafts outreach copy and validates it with moderation and outbound guardrails. The included React console streams run progress so you can follow logs, compare candidates, and approve the match end to end.

## Tech Stack
## Backend
**FastAPI** API for the workflow above, using **LangGraph**, **Pinecone** (via `langchain-pinecone`), **GPT-4o** (via `langchain-openai`), **Pydantic v2**, **OpenAI Moderation** (inbound), **guardrails-ai** (Ghostwriter wrap), and a **Postgres** LangGraph checkpointer (`langgraph-checkpoint-postgres`).

## Frontend
**React (Vite)** with **TypeScript** for the console UI, styled using **Tailwind CSS**, **shadcn/ui** components, and **Lucide React** icons. Data/state fetched with **TanStack Query (React Query)**, with agent "thinking" animations via **Framer Motion**. Real-time UI updates use native **WebSocket** or **EventSource (SSE)** hooks.


## Architecture
## Backend
- **Graph:** `researcher_node` → `auditor_node` → `human_review_node` → *(interrupt before `writer_node`)* → `writer_node` → `guardrail_validator` → (retry writer up to 3× on outbound failure or `END`).
- **HITL:** The compiled graph uses `interrupt_before=["writer_node"]`. `POST /campaign/{thread_id}/approve` sets `is_approved` / `selected_candidate_id` and schedules a background `ainvoke(None)` resume.
- **SSE:** `GET /campaign/{thread_id}/stream` **polls** `graph.aget_state` and emits JSON snapshots (it does **not** call `astream`/`ainvoke`, so it never accidentally resumes the graph before approval).

## Frontend
**Frontend**

- **App Structure:** Monorepo with `frontend/` as a Vite app (TypeScript). Core UI is a dashboard that shows agent status, campaign progress, and candidate details in modals, tables, or cards.
- **State Management:** Data fetching, mutations, and cache are managed via **TanStack Query** (React Query). App state is colocated where possible; key context (user auth, WebSocket/SSE subscriptions) via React Context and custom hooks.
- **Data Flow:** API calls via OpenAPI endpoints (`FastAPI` backend), using fetch or axios, and websocket/SSE hooks for streaming log/state updates.
- **UI/UX:** Tailwind CSS for utility-first styling, **shadcn/ui** for ready components (dialogs, toasts, skeleton loaders), and **Lucide React** for icons. Framer Motion animates agent "thinking" and progress feedback.
- **Real-time:** Subscribes to backend agent state (campaign progress, candidate status) with a native WebSocket or **EventSource (SSE)** for low-latency, robust updates, updating UI incrementally as the agent pipeline runs.

**Sample flow:**
1. Campaign creation triggers agentic pipeline; progress/status streamed to dashboard.
2. User reviews/approves candidates in UI and triggers follow-up steps.
3. All state is reactively reflected using React Query + real-time streams; no polling needed.


## Quick start (Docker)

1. Copy env: `cp backend/.env.example backend/.env` and set `OPENAI_API_KEY`, `PINECONE_API_KEY`, and index name.
2. `docker compose up --build` — the API image installs from [`backend/uv.lock`](backend/uv.lock) via `uv sync --frozen`.
3. Seed Pinecone (host network example):

```bash
docker compose run --rm -e OPENAI_API_KEY -e PINECONE_API_KEY backend \
  python scripts/seed_pinecone.py
```

4. API: `http://localhost:8000/docs`

## Local development (uv)

Dependencies and the lockfile live under **`backend/`** only.

```bash
cd backend
uv sync --extra dev
export DATABASE_URL=postgresql://langgraph:langgraph@localhost:5432/langgraph
export OPENAI_API_KEY=...
export PINECONE_API_KEY=...
unset TESTING   # use real Postgres checkpointer
uv run uvicorn app.main:app --reload --app-dir .
```

**Tests** (no Pinecone/OpenAI calls; uses `TESTING=1`, in-process `MemorySaver`, and no-op vector store until tests inject fakes):

```bash
cd backend && uv run pytest tests -v
```

To refresh the lockfile after editing `pyproject.toml`: `cd backend && uv lock`.

More detail: [backend/README.md](backend/README.md).

`conftest.py` sets `TESTING=1` before importing the app so the lifespan skips Pinecone index initialization with dummy keys.

## Quick start (frontend)

1. Run the API locally (see [Local development (uv)](#local-development-uv) or [Docker](#quick-start-docker)) so it is available at the URL you configure below.
2. Install and start the Vite app:

```bash
cd frontend
npm install
npm run dev
```

3. Open the URL Vite prints (default `http://localhost:5173`). The UI calls the FastAPI campaign routes under `VITE_API_BASE_URL` (defaults to `http://localhost:8000` if unset).

Optional: `cp frontend/.env.example frontend/.env` and set `VITE_API_BASE_URL` to your API origin (no trailing slash). You can also set the API base URL on the Settings page in the app (persisted in `localStorage`).

## AWS deployment (Terraform + GitHub Actions)

Topology (POC / dev): **React (Vite)** → **S3** (private) → **CloudFront**; **FastAPI** on **AWS App Runner** (default **`https://…awsapprunner.com`**) with a **VPC connector** to **RDS PostgreSQL** in private subnets. Infra code lives under [`infra/`](infra/).

**Note:** [App Runner will stop taking new customers after April 30, 2026](https://docs.aws.amazon.com/apprunner/latest/dg/apprunner-availability-change.html). AWS also documents a **~120s total HTTP request timeout** per request—long HITL pauses or very long **SSE** sessions may need reconnect logic for production, but the POC is fine with keepalives in [`backend/app/api/campaigns.py`](backend/app/api/campaigns.py).

### One-time bootstrap

1. From your machine, run Terraform in [`infra/bootstrap/`](infra/bootstrap/) (see [infra/bootstrap/README.md](infra/bootstrap/README.md)) to create the remote state bucket, DynamoDB lock table, and GitHub OIDC deploy role.
2. Copy [`infra/envs/dev/backend.hcl.example`](infra/envs/dev/backend.hcl.example) to `infra/envs/dev/backend.hcl` and set `bucket` / `dynamodb_table` from bootstrap outputs, then `terraform -chdir=infra/envs/dev init -backend-config=backend.hcl`.

### GitHub repository configuration

**Variables:** `AWS_REGION`, `AWS_DEPLOY_ROLE_ARN` (from bootstrap), `TF_STATE_BUCKET`, `TF_LOCK_TABLE` (same names as bootstrap outputs). Optional: `PINECONE_INDEX_NAME`, `COMPETITOR_LIST`.

**Secrets:** `OPENAI_API_KEY`, `PINECONE_API_KEY`. Optional: `LANGSMITH_API_KEY`.

Workflows: [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml) (push to `main` or manual) and [`.github/workflows/destroy.yml`](.github/workflows/destroy.yml) (manual; type `DESTROY` to confirm).

### Local deploy / destroy

```bash
cp .env.deploy.example .env.deploy   # add TF_VAR_* secrets
export AWS_REGION=us-east-1          # or put in .env.deploy
./scripts/deploy.sh
./scripts/destroy.sh DESTROY
```

### HTTPS and the browser

The production build sets **`VITE_API_BASE_URL`** to the **App Runner service URL** (`https://…`), so the **CloudFront (HTTPS) SPA** calls an **HTTPS API** and **mixed content** is avoided. The deploy workflow and [`scripts/deploy.sh`](scripts/deploy.sh) read this from `terraform output apprunner_service_url`.

### SSE and timeouts

The stream endpoint sends periodic **`: keep-alive`** SSE comments during HITL pauses (see [`backend/app/api/campaigns.py`](backend/app/api/campaigns.py)). App Runner’s **~120s** per-request cap still applies at the platform level—keep sessions within that for the POC, or add client reconnect if you outgrow it.

## API (for a React client)

### `POST /campaign/start`

```json
{ "brand_context": "We are an organic snack brand targeting US parents…" }
```

Response: `{ "thread_id": "<uuid>" }`  
Runs moderation, then runs the graph until the **interrupt before `writer_node`**.

### `GET /campaign/{thread_id}/stream`

`text/event-stream` frames:

- `data: {"type":"state_snapshot","thread_id":"…","next":["writer_node"],"values":{...}}\n\n`
- `data: {"type":"done","thread_id":"…"}\n\n` when `next` is empty (run finished).

Poll the UI on `values.logs`, `values.candidate_list`, and `next`.

### `POST /campaign/{thread_id}/approve`

```json
{ "selected_candidate_id": "cr_001" }
```

Must match a `creator_id` present in `values.candidate_list`. Returns `{ "status": "resumed" }` and resumes the graph asynchronously.

## Environment variables

See [backend/.env.example](backend/.env.example).

- **`PINECONE_EMBEDDING_MODEL`:** defaults to **`llama-text-embed-v2`** (Pinecone Inference via `PineconeEmbeddings`). Your index must match that model; see [Pinecone docs](https://docs.pinecone.io/models/llama-text-embed-v2).
- **`COMPETITOR_LIST`:** comma-separated names checked in the outbound `guardrail_validator` node (word-boundary, case-insensitive).

## Dependency note (guardrails + LangGraph)

`guardrails-ai>=0.10` is required so `langchain-core` can stay on the **1.x** line required by **LangGraph 1.1.x**. Older `guardrails-ai 0.6.x` pins `langchain-core<0.4`, which conflicts with current LangGraph releases.

## Layout

- [backend/app](backend/app) — FastAPI app, LangGraph graph, nodes, tools, schemas.
- [backend/scripts/seed_pinecone.py](backend/scripts/seed_pinecone.py) — seed demo creators.
- [docker-compose.yaml](docker-compose.yaml) — Postgres + API.
