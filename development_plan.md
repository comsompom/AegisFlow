# AegisFlow — Development Plan  
## Track 3: Programmable Stablecoin Payments (StableHacks 2026)

---

## 1. Overview & Alignment

### 1.1 Elevator Pitch (from solution)
An AI-orchestrated, permissioned stablecoin payment and treasury router on Solana. AegisFlow uses AI agents to autonomously execute FX conversions, cross-border settlements, and treasury rebalancing within a **deterministic, smart-contract-enforced compliance sandbox** (KYC, KYT, AML, Travel Rule) so execution cannot go “rogue.”

### 1.2 Mandatory Prerequisites (from description)
- **KYC** — Verify identity of participants; only KYC’d wallets can receive funds.
- **KYT** — Monitor transactions in real time; block suspicious/high-risk flows.
- **AML** — Enforce limits, controls, and reporting.
- **Travel Rule** — Collect/verify/share originator/beneficiary data above threshold (e.g. $1,000).

### 1.3 Tech Stack Summary
| Layer | Technology | Deployment Target |
|-------|------------|-------------------|
| Smart contracts | Solidity | Solana via **Neon EVM** (Devnet/Testnet) |
| Backend / AI orchestration | Python | Local / cloud (e.g. FastAPI service) |
| **Web application** | **Flask** | User-facing institutional control room |
| Compliance logic | Python + contract enforcements | Backend + on-chain |
| FX / swaps | Jupiter API (or mock) | Solana mainnet or testnet as needed |
| Custody / multi-sig (emulated) | Fireblocks-style flows | Backend + config |

**Note on Solidity on Solana:** Solidity contracts run on **Neon EVM**, which is an EVM runtime on Solana. Token Extensions (Transfer Hooks) are a **native Solana (SPL Token-2022)** feature. This plan uses Solidity on Neon for the core compliance and vault logic; equivalent behavior (whitelists, transfer checks, limits) is implemented in Solidity.

**Native Solana (recommended for hackathon):** To avoid Neon’s slow/unreliable Devnet RPC and align with “built on Solana,” use the **native Solana (Anchor)** program in **`contracts-solana/`**. It implements the same compliance registry (whitelist, blacklist, limits) in **Rust/Anchor**, deploys to **Solana Devnet** with `anchor deploy --provider.cluster devnet`, and uses Solana’s standard RPC (`api.devnet.solana.com`). See [docs/SOLANA_VS_NEON.md](docs/SOLANA_VS_NEON.md) and `contracts-solana/README.md`.

---

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                  USER-FACING WEB APP (Flask)                                 │
│  KYC • AML • Audit • Travel Rule • Transfers • Swaps • AI controls • Reports │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      PYTHON BACKEND (FastAPI)                                │
│  • AI Agent (LangChain): treasury logic, FX triggers, tx construction        │
│  • Compliance service: KYC/KYT/AML/Travel Rule checks before signing        │
│  • Travel Rule: payload generation, storage, retrieval by tx signature       │
│  • Integration: Jupiter (FX), mock Fireblocks, (optional) Chainalysis KYT   │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    ▼                   ▼                   ▼
┌───────────────────────┐  ┌───────────────────────┐  ┌───────────────────────┐
│  Neon EVM (Solana)     │  │  Off-chain DB         │  │  KYT / AML oracles    │
│  • Vault (Solidity)    │  │  • Travel Rule store  │  │  • Risk scores        │
│  • Compliance rules   │  │  • Audit events       │  │  • Sanctions/mixer    │
│  • Whitelist / limits  │  │  • Config / limits    │  │  (mock or API)        │
└───────────────────────┘  └───────────────────────┘  └───────────────────────┘
```

---

## 3. Step-by-Step Implementation

---

### Phase 1: Environment & Repo Setup

| Step | Task | Details |
|------|------|--------|
| 1.1 | Create repo structure | `contracts/` (Solidity), `backend/` (Python API), `webapp/` (Flask), `docs/` |
| 1.2 | Solidity toolchain | Node.js, Hardhat, Solidity 0.8.x; configure Hardhat for Neon EVM Devnet (RPC, chain ID 245022926) |
| 1.3 | Python environment | Python 3.11+, venv, `requirements.txt`: FastAPI, Flask, LangChain, **openai** (or langchain-openai), web3 (Neon), pydantic, httpx, (optional) Chainalysis/API clients |
| 1.4 | Neon EVM access | Wallet with test NEON (faucet), save deployer key in env (e.g. `.env`), never commit secrets |
| 1.5a | **AI / LLM (OpenAI allowed)** | Hackathon rules do **not** restrict AI providers. You may use **OpenAI** (e.g. GPT-4) for the treasury agent: set `OPENAI_API_KEY` in `.env`. Use LangChain’s OpenAI integration for the agent; key stays server-side only. |
| 1.6 | Solana testnet (if needed for Jupiter) | Configure RPC for Solana Devnet; get test USDC/EURC or use mocks |

**Deliverable:** Repo with `contracts/`, `backend/`, `webapp/`, env template; Hardhat, FastAPI, and Flask app runnable locally.

---

### Phase 2: Solidity Contracts (Neon EVM on Solana)

Deploy on **Neon EVM Devnet** (Solana test chain for EVM).

#### 2.1 Compliance & access control

| Step | Task | Details |
|------|------|--------|
| 2.1.1 | `ComplianceRegistry.sol` | Central registry: KYC whitelist (addresses allowed to receive), blacklist, optional per-address caps. |
| 2.1.2 | Roles | `OWNER`, `COMPLIANCE_OFFICER`, `AI_AGENT` (or single “operator”). Only compliance can update whitelist/blacklist; only owner can set AML global limits. |
| 2.1.3 | Events | Emit `AddressWhitelisted`, `AddressBlacklisted`, `LimitsUpdated` for audit. |

#### 2.2 Vault & transfer rules

| Step | Task | Details |
|------|------|--------|
| 2.2.1 | `AegisFlowVault.sol` | ERC-20–style vault (or wrapper) for stablecoin balances. Holds/releases tokens only to whitelisted addresses. |
| 2.2.2 | Transfer hook (in-contract) | On every transfer/withdraw: check `ComplianceRegistry.isWhitelisted(to)` and `!isBlacklisted(to)`; revert if not compliant. |
| 2.2.3 | Deposit | Allow approved entities (e.g. institutional wallets) to deposit; record balances (ERC-20 or internal accounting). |
| 2.2.4 | Withdraw / transfer | Only to whitelisted addresses; optional per-tx and daily caps enforced in contract (AML). |

#### 2.3 AML limits (deterministic sandbox)

| Step | Task | Details |
|------|------|--------|
| 2.3.1 | Global limits | In vault or registry: `maxPerTx`, `maxDailyVolume` (per agent or global). |
| 2.3.2 | Enforcement | Before executing transfer/swap, contract checks: `amount <= maxPerTx`, `dailyVolume + amount <= maxDailyVolume`; reset daily volume on a 24h boundary (e.g. by block timestamp or oracle). |
| 2.3.3 | Upgrade path | Consider `Pausable` and/or timelock for limit changes by owner. |

#### 2.4 FX / swap integration (contract side)

| Step | Task | Details |
|------|------|--------|
| 2.4.1 | Swap adapter | Contract (e.g. `AegisFlowSwap.sol`) that receives “swap” instructions from backend: e.g. approve + call a known DEX/router on Neon (or wrap Jupiter-style routing off-chain and have contract perform approve + transfer). For Neon, use existing DEX or a simple swap contract that the backend calls. |
| 2.4.2 | Slippage & limits | Enforce `minAmountOut` and/or max slippage in contract so AI cannot override; optionally cap swap size with same AML limits. |

#### 2.5 Deployment & verification

| Step | Task | Details |
|------|------|--------|
| 2.5.1 | Deploy order | Deploy `ComplianceRegistry` first, then `AegisFlowVault` (with registry address), then call `registry.setVault(vaultAddress)`. |
| 2.5.2 | **Deploy with Python** | Use **Python** (not JS): `contracts/deploy.py` compiles with **solcx** and deploys with **web3.py** to Neon Devnet. Writes `deployed.json`; copy addresses to `backend` config (e.g. `.env`). |
| 2.5.3 | Verification | Verify on NeonScan so judges can inspect. |

**Deliverable:** Solidity contracts deployed on Neon EVM (Solana test chain); backend can read whitelist and limits from contracts.

---

### Phase 3: Python Backend — Core API & Compliance

#### 3.1 FastAPI app skeleton

| Step | Task | Details |
|------|------|--------|
| 3.1.1 | Project layout | `backend/app/`: `main.py`, `config.py`, `api/`, `services/`, `agents/`, `models/`. |
| 3.1.2 | Config | Load contract addresses, RPC URLs (Neon + optional Solana), API keys (KYT, etc.) from env. |
| 3.1.3 | Health & readiness | `/health`, `/ready` (e.g. check RPC and DB if used). |

#### 3.2 Blockchain client (Neon EVM)

| Step | Task | Details |
|------|------|--------|
| 3.2.1 | Web3 client | Use `web3.py` (or similar) for Neon RPC; connect to ComplianceRegistry and AegisFlowVault. |
| 3.2.2 | Read helpers | Functions: `is_whitelisted(address)`, `get_limits()`, `get_daily_volume()`, `get_balance(vault)`. |
| 3.2.3 | Transaction building | Build and sign txs (transfer, swap) with backend wallet; ensure signer is the allowed “AI_AGENT” or operator on-chain. |

#### 3.3 Compliance service (pre-execution checks)

| Step | Task | Details |
|------|------|--------|
| 3.3.1 | KYC check | Before any transfer: resolve recipient and call contract `isWhitelisted(to)`; if false, abort and return 403. |
| 3.3.2 | KYT check | Call external KYT API (e.g. Chainalysis or mock): submit destination address and amount; if risk score above threshold, abort. Store result in audit log. |
| 3.3.3 | AML check | Ensure `amount <= maxPerTx` and `dailyVolume + amount <= maxDailyVolume` (fetch from contract or cache); abort if exceeded. |
| 3.3.4 | Travel Rule | If `amount >= TRAVEL_RULE_THRESHOLD` (e.g. 1000 USD): require payload (originator, beneficiary, VASP info); generate and store it; attach reference (e.g. tx memo or DB by tx hash). |

#### 3.4 Travel Rule implementation

| Step | Task | Details |
|------|------|--------|
| 3.4.1 | Payload schema | Define JSON schema: originator name, account, beneficiary name, account, VASP IDs, timestamp. |
| 3.4.2 | Storage | Store in DB (SQLite/Postgres) or encrypted store keyed by transaction signature; API to retrieve by tx hash for compliance dashboard. |
| 3.4.3 | Generation | When AI or API requests a transfer above threshold, backend generates payload (from authenticated user/org context), stores it, and only then proceeds to build tx; optionally include hash in memo. |

**Deliverable:** FastAPI app that can check KYC/KYT/AML/Travel Rule and build/sign Neon EVM txs.

---

### Phase 4: AI Agent (Python / LangChain)

#### 4.1 Agent role and boundaries

| Step | Task | Details |
|------|------|--------|
| 4.1.1 | Single responsibility | Agent only proposes actions (e.g. “transfer X to Y”, “swap USDC → EURC amount Z”); backend compliance layer always validates and enforces. |
| 4.1.2 | No direct key access | Agent outputs structured proposals (JSON); a separate “executor” service checks compliance and signs txs. |

#### 4.2 Treasury logic (deterministic + LLM)

| Step | Task | Details |
|------|------|--------|
| 4.2.1 | Data inputs | Mock or real FX rates (e.g. USDC/EURC), vault balances, optional yield feeds. Expose via internal API or env. |
| 4.2.2 | Rules engine | If “EURC premium > 0.5% vs USDC” then propose swap; if “treasury USD > threshold” then propose rebalance to EURC; etc. Use LangChain + **OpenAI (e.g. GPT-4)** for reasoning — hackathon allows it; set `OPENAI_API_KEY` in env and use LangChain’s `ChatOpenAI`. |
| 4.2.3 | Output schema | Proposals: `{ "action": "transfer"|"swap", "amount", "recipient"|"from_token","to_token", "reason" }`. |

#### 4.3 Execution pipeline

| Step | Task | Details |
|------|------|--------|
| 4.3.1 | Proposal → compliance | Backend receives proposal; runs KYC/KYT/AML/Travel Rule; if any check fails, return error to agent (and log). |
| 4.3.2 | Execution | If passed: build Neon EVM tx (transfer or swap), sign, broadcast; store tx hash and link Travel Rule if applicable. |
| 4.3.3 | Audit | Log every proposal and outcome (allowed/denied, reason, tx hash) for dashboard. |

**Deliverable:** AI agent that proposes treasury/FX actions; backend enforces sandbox and executes only compliant txs.

---

### Phase 5: Integrations & Mocks

| Step | Task | Details |
|------|------|--------|
| 5.1 | Jupiter (or Neon DEX) | Backend calls Jupiter API (or Neon DEX) for swap route; build tx that calls your Swap adapter or router; enforce slippage in contract. |
| 5.2 | KYT | Integrate Chainalysis/Elliptic API or mock: input address + amount, return risk score; block if above threshold. |
| 5.3 | Fireblocks-style | Emulate multi-sig: e.g. “sensitive” actions (limit change, whitelist) require second approval (mock: second API key or manual step in dashboard). |
| 5.4 | FX feed | Use public API or mock for USDC/EURC rates so agent has data to decide. |

**Deliverable:** Backend can perform real or mocked FX swaps and KYT; optional multi-sig emulation for high-privilege actions.

---

### Phase 6: User-Friendly Flask Web Application (Institutional Control Room)

A **well-developed, user-friendly Flask web app** where users (compliance officers, treasury operators, auditors) can perform **all** AegisFlow operations described in this plan. The webapp is the single entry point for configuration, execution, and monitoring.

#### 6.1 Flask app foundation & UX principles

| Step | Task | Details |
|------|------|--------|
| 6.1.1 | Project layout | `webapp/`: `app.py`, `config.py`, `routes/`, `templates/`, `static/` (CSS, JS, images), `forms/`, `utils/`. Use Flask blueprints for modular routes (e.g. `auth`, `compliance`, `treasury`, `audit`). |
| 6.1.2 | Design system | Consistent UI: clear navigation (sidebar or top nav), role-based menus, success/error flash messages, loading states, responsive layout (Bootstrap 5 or Tailwind CSS). Use a professional, institutional look (clean typography, accessible contrast). |
| 6.1.3 | Authentication & roles | Flask-Login (or similar): login/logout, session management. Roles: **Compliance Officer**, **Treasury Operator**, **Auditor**, **Admin**. Restrict actions by role (e.g. only Compliance can whitelist; only Admin can set AML limits). |
| 6.1.4 | API integration | Webapp calls the **FastAPI backend** (REST or internal) for all blockchain and AI operations. No private keys in the webapp; backend holds signer and performs compliance checks. |

#### 6.2 KYC (Whitelist) management

| Step | Task | Details |
|------|------|--------|
| 6.2.1 | Whitelist page | **List view**: table of whitelisted addresses with optional labels, KYC status, date added; search/filter; pagination. |
| 6.2.2 | Add address | Form: wallet address, label (e.g. "AMINA Bank custody"), optional per-address cap. Validation (checksum). Submit → backend updates ComplianceRegistry (Compliance Officer only). Success/error feedback. |
| 6.2.3 | Remove / blacklist | "Remove from whitelist" and "Add to blacklist" actions with confirmation modal. Backend updates contract. |
| 6.2.4 | Bulk import | Optional: CSV upload for multiple addresses (with validation) for onboarding. |

#### 6.3 AML limits & controls

| Step | Task | Details |
|------|------|--------|
| 6.3.1 | Limits page | Display current **maxPerTx**, **maxDailyVolume** (and daily used volume), optional per-agent caps. Clear readout (e.g. "Daily remaining: X USDC"). |
| 6.3.2 | Edit limits | Form to update maxPerTx and maxDailyVolume (Admin/Owner only). Confirmation step; optional multi-sig emulation (second approver). Backend submits tx to contract. |
| 6.3.3 | Pause / resume | Button to pause AI agent or vault withdrawals (if contract supports Pausable); show current state. |

#### 6.4 Manual transfers & swaps (user-initiated)

| Step | Task | Details |
|------|------|--------|
| 6.4.1 | Transfer page | Form: recipient (dropdown of whitelisted or address input with live whitelist check), amount, token (USDC/EURC), optional memo. For amounts ≥ Travel Rule threshold: **Travel Rule form** (originator, beneficiary, VASP info) inline. Submit → backend runs KYC/KYT/AML/Travel Rule, then executes. Show tx hash and status. |
| 6.4.2 | Swap (FX) page | Form: from token, to token, amount, max slippage. Preview (e.g. "You will receive ~X EURC"). Submit → backend routes via Jupiter/Neon DEX, enforces limits, executes. Display result and tx link. |
| 6.4.3 | Validation & errors | Client-side validation (amount > 0, valid address); server-side errors (e.g. "Recipient not whitelisted", "Daily limit exceeded") shown clearly with suggested actions. |

#### 6.5 AI agent control & treasury

| Step | Task | Details |
|------|------|--------|
| 6.5.1 | AI status dashboard | Card/section: "AI Treasury Agent" — status (running/paused), last run time, next scheduled run. Buttons: **Start / Pause / Run once**. |
| 6.5.2 | Proposals feed | List of **recent AI proposals**: time, action (transfer/swap), amount, recipient/tokens, reason (e.g. "EURC premium 0.6%"), status (pending/approved/rejected). Optional: "Approve" / "Reject" for manual override (if workflow requires human-in-the-loop). |
| 6.5.3 | Trigger rules (view/edit) | Page to view (and optionally edit) rules that trigger the AI (e.g. "Swap when EURC premium > 0.5%"). Form or table; changes stored in backend config. |

#### 6.6 Audit log & reporting

| Step | Task | Details |
|------|------|--------|
| 6.6.1 | Audit log page | **Filterable table**: timestamp, action type (transfer/swap/whitelist/limit change), actor (user or AI), amount, counterparty, status (success/denied), tx hash (link to explorer), reason if denied. Export to CSV. |
| 6.6.2 | Travel Rule viewer | **Search by tx hash** or date range. Display stored Travel Rule payload: originator name, account, beneficiary name, account, VASP IDs, timestamp. Compliance/Auditor role. |
| 6.6.3 | Summary widgets | Dashboard homepage: total volume today, number of txs, whitelist size, alerts (e.g. "Daily limit 80% used"). |

#### 6.7 Additional UX & polish

| Step | Task | Details |
|------|------|--------|
| 6.7.1 | Home / dashboard | Single landing page after login: key metrics, quick actions (New transfer, View audit log), recent activity, system status (backend health, chain connection). |
| 6.7.2 | Help & tooltips | Short tooltips or "?" icons for compliance terms (KYC, Travel Rule threshold); optional "Help" or "Docs" page. |
| 6.7.3 | Error handling | Friendly error pages (404, 500); API timeout handling with "Retry" option; session expiry redirect to login. |
| 6.7.4 | Accessibility | Semantic HTML, ARIA where needed, keyboard navigation, sufficient color contrast (WCAG 2.1 AA target). |

**Deliverable:** Full-featured Flask webapp where users can manage KYC whitelist, set AML limits, perform manual transfers/swaps with Travel Rule, control the AI agent, view proposals, and access full audit log and Travel Rule data.

#### Webapp feature checklist (user can do everything here)

| Area | User can… |
|------|-----------|
| **Auth** | Log in / log out; see role-based menu and restrictions. |
| **KYC** | View whitelist; add/remove addresses; add to blacklist; optional bulk import. |
| **AML** | View current limits and daily usage; edit maxPerTx and maxDailyVolume (Admin); pause/resume if supported. |
| **Transfers** | Submit manual stablecoin transfer (recipient, amount, token); fill Travel Rule form when above threshold; see tx result and explorer link. |
| **Swaps (FX)** | Submit swap (from/to token, amount, slippage); see preview and result; link to tx. |
| **AI agent** | See agent status; start/pause/run once; view recent proposals; optionally approve/reject; view/edit trigger rules. |
| **Audit** | View filterable audit log (all actions, status, tx hash); export CSV; search Travel Rule by tx hash and view payload. |
| **Dashboard** | See summary metrics, recent activity, quick actions, system health. |

---

### Phase 7: Testing & Hardening

| Step | Task | Details |
|------|------|--------|
| 7.1 | Unit tests (contracts) | Hardhat: whitelist allow/deny, limit enforcement, role access. |
| 7.2 | Unit tests (backend) | Pytest: compliance service (mock contract), Travel Rule generation, agent output parsing. |
| 7.3 | Webapp tests | Flask test client or pytest: login, role-based redirects, form validation; optional E2E (e.g. Playwright) for critical flows (whitelist, transfer, audit). |
| 7.4 | Integration | E2E: agent proposes → backend checks → contract reverts if non-whitelisted; then whitelist and retry → success; verify audit log and Travel Rule in webapp. |
| 7.5 | Security | No secrets in repo; env-based keys; rate limiting on API and webapp; input validation on all endpoints and forms; CSRF protection (Flask-WTF). |

**Deliverable:** Test suite and at least one E2E flow on Neon Devnet.

---

### Phase 8: Deployment & Demo

| Step | Task | Details |
|------|------|--------|
| 8.1 | Contracts | Deploy to Neon EVM Devnet (Solana test chain); document addresses and NeonScan links. |
| 8.2 | Backend | Run as service (e.g. Docker); use env for RPC, contract addresses, API keys. |
| 8.3 | Webapp | Run Flask app (e.g. Gunicorn in production); ensure it talks to backend API; document login and role-based access. |
| 8.4 | Demo script | 1) Log in to webapp; 2) Add/remove whitelist; 3) Set AML limits; 4) Submit transfer (with Travel Rule for large amount); 5) Run AI agent and show proposals; 6) View audit log and Travel Rule by tx hash; 7) Show blocked non-whitelisted attempt. |
| 8.5 | Video & README | 3-min Loom: problem (AI + compliance), solution (sandbox), demo via Flask webapp on testnet; README with setup for backend + webapp. |

**Deliverable:** Testnet deployment, Flask webapp live, demo script, and submission-ready repo + video.

---

## 4. File Structure (Suggested)

```
AegisFlow/
├── contracts/                    # Solidity (Neon EVM)
│   ├── contracts/
│   │   ├── ComplianceRegistry.sol
│   │   ├── AegisFlowVault.sol
│   │   └── AegisFlowSwap.sol     # optional
│   ├── deploy.py           # Python deployment (solcx + web3.py)
│   ├── requirements.txt   # web3, solcx, python-dotenv
│   ├── script/
│   │   └── deploy.js       # optional (reference only)
│   ├── test/
│   ├── hardhat.config.js
│   └── package.json
├── backend/                      # Python API (FastAPI)
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/
│   │   ├── services/
│   │   │   ├── compliance.py
│   │   │   ├── blockchain.py
│   │   │   └── travel_rule.py
│   │   └── agents/
│   │       └── treasury_agent.py
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── webapp/                       # Flask user-facing web application
│   ├── app.py
│   ├── config.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── compliance.py         # KYC whitelist, blacklist
│   │   ├── limits.py             # AML limits
│   │   ├── transfers.py          # manual transfer, swap
│   │   ├── ai_agent.py           # AI status, proposals
│   │   └── audit.py              # audit log, Travel Rule viewer
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── whitelist.html
│   │   ├── limits.html
│   │   ├── transfer.html
│   │   ├── swap.html
│   │   ├── audit.html
│   │   └── travel_rule.html
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   ├── forms/
│   ├── utils/
│   ├── requirements.txt
│   └── .env.example
├── description.md
├── solution.md
└── development_plan.md           # this file
```

---

## 5. Compliance Sandbox Summary

| Requirement | Where enforced | How |
|-------------|----------------|------|
| **KYC** | On-chain (Solidity) | Transfer/withdraw only to `ComplianceRegistry` whitelist; backend checks before building tx. |
| **KYT** | Backend + optional on-chain | Backend calls KYT API; if high risk, backend does not sign; optionally store risk result on-chain or in audit log. |
| **AML** | On-chain (Solidity) | `maxPerTx`, `maxDailyVolume` in contract; revert if exceeded; backend checks first. |
| **Travel Rule** | Backend + storage | Backend generates and stores payload for txs above threshold; dashboard shows by tx hash; optional hash in memo. |

---

## 6. Success Criteria for MVP

- [ ] Solidity contracts deployed on Neon EVM (Solana test chain).
- [ ] Python backend: compliance checks (KYC/KYT/AML/Travel Rule) and tx building/signing for Neon.
- [ ] AI agent proposes treasury/FX actions; execution only after passing all checks.
- [ ] At least one E2E flow: compliant transfer and one blocked (e.g. non-whitelisted) with clear revert/error.
- [ ] Travel Rule payload generated and retrievable for a transfer above threshold.
- [ ] **Flask webapp:** Users can perform all operations from the UI: login, manage KYC whitelist, set AML limits, submit transfers/swaps (with Travel Rule when required), control AI agent, view audit log and Travel Rule data.
- [ ] README and 3-minute demo video explaining problem, solution, and testnet demo (including webapp walkthrough).

---

## 7. References

- **Neon EVM on Solana:** https://neonevm.org/docs/developing/get-started  
- **Hardhat + Neon:** https://neonevm.org/docs/developing/deploy_facilities/using_hardhat  
- **StableHacks 2026:** description.md (tracks, prerequisites), solution.md (AegisFlow concept).  
- **Token Extensions (future):** If moving to native Solana SPL tokens, implement Transfer Hooks in an Anchor program and keep this Solidity layer for Neon-based flows or bridge logic.

---

### 7.1 Use of OpenAI (and other AI providers)

**StableHacks 2026 rules do not restrict which AI or LLM providers you use.** The description requires building on Solana, an MVP, and compliance (KYC/KYT/AML/Travel Rule); it does not forbid third-party APIs or specify AI vendors. Track 3 explicitly encourages "AI agents" for programmable payments.

**You may use OpenAI** (e.g. GPT-4 or GPT-4o) for the AegisFlow treasury agent. Store `OPENAI_API_KEY` in environment variables (e.g. `.env`); never commit it. Use LangChain’s OpenAI integration (`langchain-openai`, `ChatOpenAI`) in the backend so the key stays server-side. This is compliant with the hackathon and aligns with the “AI-orchestrated” design in the solution.

---

*Document version: 1.2 — AegisFlow development plan for Track 3 (Programmable Stablecoin Payments), StableHacks 2026. Includes Flask webapp; OpenAI use explicitly permitted.*
