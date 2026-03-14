# AegisFlow Backend (FastAPI)

API for compliance checks, transfers, audit log, Travel Rule, and AI treasury agent. **SQLite is required**: audit log and Travel Rule payloads are stored in `aegisflow.db` (created automatically on first run).

## Setup

```bash
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env: NEON_RPC_URL, contract addresses, OPENAI_API_KEY (optional). DATABASE_URL defaults to sqlite:///./aegisflow.db
```

## Run

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs

## Endpoints

- `GET /health`, `GET /health/ready` — health check
- `GET/POST /api/compliance/whitelist/{address}`, `POST /api/compliance/limits` — KYC/AML
- `POST /api/transfers/check`, `POST /api/transfers/execute` — transfer compliance and execute
- `GET /api/audit/log`, `GET /api/audit/travel-rule/{tx_hash}` — audit and Travel Rule
- `GET /api/ai/status`, `POST /api/ai/run-once`, `GET /api/ai/proposals` — AI agent
