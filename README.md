# Multi-agent claims pipeline

Plum-style **health insurance claims** assignment: staged pipeline, **policy from [`policy_terms.json`](policy_terms.json)**, **official cases in [`test_cases.json`](test_cases.json)**, dual trace (ops + LLM), Redis-backed workers, Streamlit UI.

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
cp .env.example .env        # add GEMINI_API_KEY for live extraction
docker compose up -d redis

# Terminal 1 — API
uvicorn claims_pipeline.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 — LLM worker (Gemini)
python -m claims_pipeline.workers.llm_worker

# Terminal 3 — Claim worker
python -m claims_pipeline.workers.claim_worker

# Terminal 4 — UI
streamlit run src/claims_pipeline/streamlit_app.py
```

### Docker (full stack)

Copy env and add **`GEMINI_API_KEY`** (required for the LLM worker).

```bash
cp .env.example .env
# edit .env — set GEMINI_API_KEY at minimum

docker compose build
docker compose up -d
```

- **API**: [http://localhost:8000](http://localhost:8000) · **Streamlit**: [http://localhost:8501](http://localhost:8501) · **Redis**: `localhost:6379`  
- SQLite data persists in the **`claims_sqlite`** Docker volume.  
- Streamlit uses **`CLAIMS_API_URL=http://api:8000`** inside the stack and **`PUBLIC_CLAIMS_API_URL=http://localhost:8000`** for browser-facing links (CSV); override in compose if you publish the API behind another host or TLS.

For **local iteration** with hot reload, keep using Redis only (`docker compose up -d redis`) and run API/workers/UI on the host as above.

## Tests & eval

```bash
pytest tests/ -v
python scripts/run_eval.py
python scripts/run_robustness_eval.py
```

- [`docs/EVAL_REPORT.md`](docs/EVAL_REPORT.md) — fixture run (no LLM).
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md), [`docs/COMPONENT_CONTRACTS.md`](docs/COMPONENT_CONTRACTS.md).

## Layout

- `Dockerfile`, `docker-compose.yml` — one image; Compose runs Redis and optionally API + workers + Streamlit.
- `src/claims_pipeline/` — FastAPI (`main.py`), orchestrator, agents, DB, Gemini + Redis LLM bridge, workers, Streamlit (`streamlit_app.py`).
- `tests/` — pytest suites.
- `scripts/` — eval and fixture helpers.
- `docs/` — architecture, contracts, eval reports, demo checklist.

## Model

Default **`gemini-3-flash-preview`** (`LLM_MODEL`). Override in `.env`.
