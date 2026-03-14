# AegisFlow Web Application (Flask)

User-facing institutional control room for AegisFlow: KYC whitelist, AML limits, transfers, AI agent control, audit log, and Travel Rule viewer.

## Setup

```bash
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Set BACKEND_API_URL to your FastAPI backend (e.g. http://localhost:8000)
# Set SECRET_KEY (e.g. python -c "import secrets; print(secrets.token_hex(32))")
# Optional: DEMO_USER, DEMO_PASSWORD for login (default: compliance / demo123)
```

## Run

Ensure the **backend** (FastAPI) is running first (e.g. `uvicorn app.main:app --port 8000` in the `backend/` folder).

```bash
flask run
# or: python app.py
```

Open http://localhost:5000. Log in with the demo user, then use the nav to access Dashboard, KYC Whitelist, AML Limits, Transfer, AI Agent, Audit Log, and Travel Rule.

## Features

- **Login** — Demo user (configurable via .env).
- **Dashboard** — Limits summary and quick actions.
- **KYC Whitelist** — Add/remove/blacklist addresses (calls backend API).
- **AML Limits** — View and update max per-tx and daily volume.
- **Transfer** — Submit transfer with optional Travel Rule fields.
- **AI Agent** — Status, Run once, view proposals.
- **Audit Log** — List of actions and outcomes.
- **Travel Rule** — Search by tx hash and view stored payloads.
