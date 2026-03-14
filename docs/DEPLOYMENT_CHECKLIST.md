# AegisFlow — Deployment checklist (Solana)

Hackathon requirement: **build on Solana**. This project uses **native Solana** (Anchor) on **Solana Devnet**.

---

## Deploy all and verify (summary)

1. **Install tools (once):** Rust, [Solana CLI](https://docs.solana.com/cli/install), [Anchor CLI](https://www.anchor-lang.com/docs/installation). On Windows: use WSL (Ubuntu) and run the [one-line Solana install](https://solana.com/docs/intro/installation) (installs Solana + Anchor), or install Rust (e.g. `winget install Rustlang.Rustup`) then Solana CLI and `cargo install anchor-cli`.
2. **Deploy program:** From repo root run `.\scripts\deploy_solana_devnet.ps1` (or run the commands in Step 1 below manually).
3. **Backend .env:** Set `SOLANA_PROGRAM_ID`, `SOLANA_RPC_URL`, and `SOLANA_KEYPAIR_PATH` (or `SOLANA_PRIVATE_KEY`).
4. **Initialize program (once):** `cd backend && python -m scripts.init_solana_program`
5. **Start backend:** `cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000`
6. **Start webapp:** `cd webapp && flask run` → open http://localhost:5000
7. **Verify:** `.\scripts\verify_stack.ps1` (checks backend imports; if server is running, checks `/health`).

---

## Required env

| Location | Required | Optional |
|----------|----------|----------|
| **backend/.env** | `SOLANA_RPC_URL`, `SOLANA_PROGRAM_ID` | `SOLANA_KEYPAIR_PATH` or `SOLANA_PRIVATE_KEY` (for submitting txs), `OPENAI_API_KEY`, `DATABASE_URL` |
| **webapp/.env** | `BACKEND_API_URL`, `SECRET_KEY` | `DEMO_USER`, `DEMO_PASSWORD` |

Program ID comes from **contracts-solana** after `anchor build` / `anchor keys list`.

---

## Step 1: Deploy program (Solana Devnet)

From repo root:

```bash
cd contracts-solana
solana config set --url devnet
solana airdrop 2
anchor build
anchor keys list    # copy the program ID → backend .env SOLANA_PROGRAM_ID
anchor deploy --provider.cluster devnet
```

- You need SOL on Devnet ([Solana faucet](https://faucet.solana.com/)).
- After deploy, **initialize** the program once from the backend (with `.env` set):  
  `cd backend && python -m scripts.init_solana_program`  
  This runs `init_config`, `init_vault`, and `set_vault`. Alternatively use the Anchor TS client (see `contracts-solana/README.md`).

---

## Step 2: Backend .env

In **backend/.env** set:

- `SOLANA_RPC_URL=https://api.devnet.solana.com`
- `SOLANA_PROGRAM_ID=<program-id-from-step-1>`
- `SOLANA_KEYPAIR_PATH=~/.config/solana/id.json` (or `SOLANA_PRIVATE_KEY=...`) so the backend can submit whitelist/limits/vault_withdraw transactions.

---

## Step 3: Start backend

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- SQLite and tables are created on first run.
- Check: http://localhost:8000/health → `{"status":"ok"}`
- Check: http://localhost:8000/docs

---

## Step 4: Start webapp

```bash
cd webapp
flask run
```

Open http://localhost:5000, log in (e.g. demo user), then use Dashboard, Whitelist, Limits, Transfer, AI agent, Audit.

---

## Step 5: Smoke test

1. **Backend:** `GET /health`, `GET /api/compliance/limits` (returns limits from chain once config is initialized).
2. **Webapp:** Log in → add address to whitelist (needs `SOLANA_KEYPAIR_PATH` or `SOLANA_PRIVATE_KEY` for tx).
3. **Transfer:** Execute a transfer to a whitelisted address (amount in lamports); backend calls `vault_withdraw` on Solana when signer is configured.

---

## Troubleshooting

- **"Solana program not configured"** — set `SOLANA_PROGRAM_ID` in backend/.env.
- **Whitelist/limits tx fails** — ensure keypair has SOL on Devnet and is the program authority.
- **RPC errors** — use `https://api.devnet.solana.com` or another Devnet RPC from [Solana docs](https://docs.solana.com/cluster/rpc-endpoints).
