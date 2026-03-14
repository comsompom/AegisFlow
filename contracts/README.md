# AegisFlow — Smart Contracts (Neon EVM)

Solidity contracts for the AegisFlow compliance sandbox, deployable on **Neon EVM** (Solana).

## Contracts

- **ComplianceRegistry** — KYC whitelist/blacklist, AML limits (maxPerTx, maxDailyVolume), roles (owner, compliance officer, AI agent, vault).
- **AegisFlowVault** — ERC-20 style vault; transfers/withdrawals only to whitelisted addresses; calls registry for compliance checks.

## Deployment (Python)

Deployment is done with **Python** (web3.py + solcx). No Node/JavaScript required for deploying.

### Setup

```bash
cd contracts
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Set PRIVATE_KEY (deployer wallet with test NEON from https://neonfaucet.org)
# Optionally set NEON_RPC_URL (default: https://devnet.neonevm.org)
```

### Deploy

```bash
python deploy.py
```

This will:

1. Compile `contracts/ComplianceRegistry.sol` and `contracts/AegisFlowVault.sol` with solc 0.8.20.
2. Deploy ComplianceRegistry (with deployer as compliance officer and AI agent, default limits).
3. Deploy AegisFlowVault (with registry address and deployer as treasury).
4. Call `registry.setVault(vault_address)`.
5. Write **deployed.json** with contract addresses.

Use the addresses in **backend** `.env`: `COMPLIANCE_REGISTRY_ADDRESS`, `AEGISFLOW_VAULT_ADDRESS`.

## Build & test (optional — Hardhat)

For compilation and unit tests you can still use Hardhat (Node.js):

```bash
npm install
npx hardhat compile
npx hardhat test
```

The JavaScript deploy script (`scripts/deploy.js`) is kept for reference but **Python deploy.py is the supported way to deploy**.

## Networks

- **Neon Devnet** — Chain ID 245022926, RPC https://devnet.neonevm.org
- **Neon Mainnet** — Chain ID 245022934 (set `NEON_RPC_URL` to mainnet RPC; use with care)
