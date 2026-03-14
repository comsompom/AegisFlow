# AegisFlow

!["AegisFlow Logo"](aegis_flow_logo.jpg)

**Track 3: Programmable Stablecoin Payments** — StableHacks 2026

An AI-orchestrated, permissioned stablecoin payment and treasury router on Solana. AegisFlow uses AI agents to autonomously execute FX conversions, cross-border settlements, and treasury rebalancing within a **deterministic, smart-contract-enforced compliance sandbox** (KYC, KYT, AML, Travel Rule).

---

## Project structure

```
AegisFlow/
├── aegis_flow_logo.png # App logo
├── contracts/          # Solidity smart contracts (Neon EVM on Solana) — optional
├── contracts-solana/   # Native Solana (Anchor/Rust) — deploy to Solana Devnet (recommended)
├── backend/            # Python FastAPI — compliance, AI agent, blockchain client
├── webapp/             # Flask web application — institutional control room UI
├── docs/               # development_plan, solution, SOLANA_VS_NEON
└── README.md
```

---

## Prerequisites

- **Python** 3.11+ and **pip** (for backend and webapp; also for Neon contract deploy if using Option B)
- **For native Solana (Option A):** Rust, [Solana CLI](https://docs.solana.com/cli/install), [Anchor CLI](https://www.anchor-lang.com/docs/installation); Solana wallet (e.g. Phantom) or `solana-keygen` for deploy
- **For Neon EVM (Option B):** Node.js 18+ (optional), **MetaMask** and private key; add [Neon EVM Devnet](https://neonfaucet.org). See [Wallet & private keys](docs/WALLET_AND_KEYS.md)
- **OpenAI API key** (optional, for AI treasury agent)

---

## Quick start

### 1. Clone and environment

```bash
git clone <repo-url>
cd AegisFlow
```

### 2. Smart contracts

**Option A — Native Solana (recommended):** Deploy to Solana Devnet (no Neon).

```bash
cd contracts-solana
# Install: Rust, Solana CLI, Anchor CLI (see contracts-solana/README.md)
solana config set --url devnet
solana airdrop 2
anchor build
anchor deploy --provider.cluster devnet
# Use the program ID and ComplianceConfig PDA in backend .env (see docs/SOLANA_VS_NEON.md)
cd ..
```

**Option B — Neon EVM (Solidity):** Uses Neon’s Devnet (can be slow).

```bash
cd contracts
python -m venv venv
# Windows: venv\Scripts\activate  |  macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env: set PRIVATE_KEY, NEON_RPC_URL (e.g. https://devnet.neonevm.org)
python deploy.py
# Addresses in deployed.json → backend .env (COMPLIANCE_REGISTRY_ADDRESS, AEGISFLOW_VAULT_ADDRESS)
cd ..
```

### 3. Backend (FastAPI)

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env: NEON_RPC_URL, contract addresses, OPENAI_API_KEY (optional)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# API: http://localhost:8000
cd ..
```

### 4. Web application (Flask)

```bash
cd webapp
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env: BACKEND_API_URL=http://localhost:8000 (or your backend URL)
flask run
# Webapp: http://localhost:5000
cd ..
```

### 5. First use

1. Open **http://localhost:5000** in a browser.
2. Log in (default demo user if configured; see `webapp/README.md`).
3. Add a whitelisted address (KYC), set AML limits, then try a transfer or run the AI agent.

---

## Features

| Feature | Description |
|--------|-------------|
| **KYC** | Whitelist/blacklist addresses; only whitelisted can receive funds (enforced on-chain). |
| **AML** | Configurable max per-tx and daily volume; enforced in smart contracts. |
| **KYT** | Optional integration with risk APIs; high-risk destinations blocked before execution. |
| **Travel Rule** | For transfers above threshold: originator/beneficiary data stored and viewable by tx hash. |
| **AI agent** | Treasury agent proposes transfers/swaps; execution only after compliance checks. |
| **Audit** | Full log of actions, proposals, and Travel Rule data in the webapp. |

---

## Tech stack

- **Contracts:** Solidity, Hardhat, Neon EVM (Solana)
- **Backend:** Python, FastAPI, LangChain, OpenAI (optional), Web3.py
- **Webapp:** Flask, Jinja2, Bootstrap 5

---

## Documentation

- [Deployment checklist](docs/DEPLOYMENT_CHECKLIST.md) — required env, deploy contracts, start backend & webapp, smoke test
- [Wallet & private keys](docs/WALLET_AND_KEYS.md) — where to get your MetaMask private key and where to use it
- [Development plan](development_plan.md) — full implementation plan
- [Solution concept](solution.md) — AegisFlow concept and compliance sandbox
- [Hackathon description](description.md) — StableHacks 2026 tracks and rules

---

## License

See repository license. Built for StableHacks 2026 (Track 3: Programmable Stablecoin Payments).
