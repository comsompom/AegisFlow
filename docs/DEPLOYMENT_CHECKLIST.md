# AegisFlow — Deployment checklist

## Required env (you have updated these)

| Location | Required | Optional |
|----------|----------|----------|
| **contracts/.env** | `PRIVATE_KEY` | `NEON_RPC_URL` (default: https://devnet.neonevm.org) |
| **backend/.env** | `PRIVATE_KEY`, `COMPLIANCE_REGISTRY_ADDRESS`, `AEGISFLOW_VAULT_ADDRESS` | `NEON_RPC_URL`, `DATABASE_URL`, `OPENAI_API_KEY` |
| **webapp/.env** | `BACKEND_API_URL`, `SECRET_KEY` | `DEMO_USER`, `DEMO_PASSWORD` |

Contract addresses come from **contracts/deployed.json** after a successful deploy.

---

## Step 1: Deploy contracts (Neon EVM Devnet)

From repo root:

```bash
cd contracts
python deploy.py
```

- You need NEON tokens on Devnet (you have these).
- If you see **Read timed out**: Neon public RPC can be slow. Wait a few minutes and run `python deploy.py` again. Timeouts in the script are set to 120s.
- On success you get **contracts/deployed.json** with `ComplianceRegistry` and `AegisFlowVault` addresses.

To copy addresses into backend env:

```bash
python apply_deployed.py
```

Then add the two lines it prints to **backend/.env** (or copy from **contracts/deployed.json** by hand).

---

## Step 2: Start backend

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- SQLite DB and tables are created on first run.
- Check: http://localhost:8000/health → `{"status":"ok"}`
- Check: http://localhost:8000/docs

---

## Step 3: Start webapp

```bash
cd webapp
flask run
```

- Set `FLASK_APP=app:app` if needed. Open http://localhost:5000, log in (e.g. compliance / demo123), then use Dashboard, Whitelist, Transfer, etc.

---

## Step 4: Quick smoke test

1. **Backend:** `GET /health` and `GET /api/audit/log` (can be empty).
2. **Webapp:** Log in → Dashboard → add an address to whitelist (backend must have contract addresses and `PRIVATE_KEY` for the tx to be submitted).
3. **Contracts:** With addresses in backend .env, `/api/compliance/limits` should return real limits from chain.

If deploy keeps timing out, run `python deploy.py` from **contracts/** in your own terminal and watch the output; retry when the Neon RPC is responsive.
