# AegisFlow

!["AegisFlow Logo"](aegis_flow_logo.jpg)

**Track 3: Programmable Stablecoin Payments** — StableHacks 2026

An AI-orchestrated, permissioned stablecoin payment and treasury router **on Solana**. AegisFlow uses AI agents to autonomously execute FX conversions, cross-border settlements, and treasury rebalancing within a **deterministic, smart-contract-enforced compliance sandbox** (KYC, KYT, AML, Travel Rule). **User-facing layer is 100% Python:** API (FastAPI) and UI (Flask). On-chain: native Solana (Anchor) for the hackathon.

---

## Project structure

```
AegisFlow/
├── aegis_flow_logo.png
├── contracts-solana/   # Native Solana (Anchor/Rust) — deploy to Solana Devnet
├── backend/            # Python FastAPI — Solana client, compliance, AI agent
├── webapp/             # Flask web application — institutional control room UI
├── docs/
└── README.md
```

---

## Prerequisites

- **Python** 3.11+ and **pip**
- **Rust**, [Solana CLI](https://docs.solana.com/cli/install), [Anchor CLI](https://www.anchor-lang.com/docs/installation)
- **Solana wallet** (e.g. Phantom) or `solana-keygen` for deployment and backend signer
- **OpenAI API key** (optional, for AI treasury agent)

---

## Quick start

### 1. Clone

```bash
git clone <repo-url>
cd AegisFlow
```

### 2. Deploy program to Solana Devnet

**Prereq:** Install [Rust](https://rustup.rs/), [Solana CLI](https://docs.solana.com/cli/install), [Anchor CLI](https://www.anchor-lang.com/docs/installation). On Windows, WSL (Ubuntu) is recommended; see [Deployment checklist](docs/DEPLOYMENT_CHECKLIST.md).

From repo root (PowerShell):

```powershell
.\scripts\deploy_solana_devnet.ps1
```

Or manually:

```bash
cd contracts-solana
solana config set --url devnet
solana airdrop 2
anchor build
anchor keys list   # note the program ID
anchor deploy --provider.cluster devnet
cd ..
```

After deploy, note the **program ID** (e.g. from `anchor keys list`).

### 3. Backend (FastAPI)

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate  |  macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit **.env**:

- `SOLANA_RPC_URL=https://api.devnet.solana.com`
- `SOLANA_PROGRAM_ID=<program-id-from-step-2>`
- `SOLANA_KEYPAIR_PATH=~/.config/solana/id.json` (or set `SOLANA_PRIVATE_KEY` for signer)

Then:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API: http://localhost:8000

### 4. Web application (Flask)

```bash
cd webapp
python -m venv venv
# Windows: venv\Scripts\activate  |  macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env: BACKEND_API_URL=http://localhost:8000
flask run
```

Webapp: http://localhost:5000

### 5. Initialize program (once)

From the **backend** directory (with `.env` set):

```bash
cd backend
python -m scripts.init_solana_program
```

This creates the compliance config and vault PDAs on-chain.

### 6. First use

1. Open **http://localhost:5000**, log in (demo user if configured).
2. Add a whitelisted address (KYC), set AML limits, then try a transfer or run the AI agent.

---

## Features

| Feature | Description |
|--------|-------------|
| **KYC** | Whitelist/blacklist addresses on Solana; only whitelisted can receive (enforced on-chain). |
| **AML** | Configurable max per-tx and daily volume; enforced in the Anchor program. |
| **KYT** | Optional risk API integration; high-risk destinations blocked before execution. |
| **Travel Rule** | For transfers above threshold: originator/beneficiary data stored and viewable by tx hash. |
| **AI agent** | Treasury agent proposes transfers; execution only after compliance checks. |
| **Audit** | Full log of actions, proposals, and Travel Rule data in the webapp. |

---

## Tech stack

- **On-chain:** Rust, Anchor — native Solana program on **Solana Devnet**
- **API & UI (Python only):** FastAPI (backend API), Flask (web UI), LangChain, OpenAI (optional), Solana/solders for chain

---

## Documentation

- [Deployment checklist](docs/DEPLOYMENT_CHECKLIST.md) — env, deploy program, start backend & webapp
- [Development plan](development_plan.md) — implementation plan
- [Solution concept](solution.md) — AegisFlow and compliance sandbox
- [Hackathon description](description.md) — StableHacks 2026 rules

All user-facing visualization and API are in **Python** (Flask + FastAPI).

---

## License

See repository license. Built for StableHacks 2026 (Track 3: Programmable Stablecoin Payments). **All projects must be built on Solana** — this repo uses native Solana (Anchor) on Solana Devnet.
