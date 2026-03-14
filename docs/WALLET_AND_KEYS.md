# Wallet & Private Keys for AegisFlow

You need **one Ethereum-compatible wallet** (e.g. **MetaMask**) for deploying contracts and for the backend to sign transactions. Use the **same wallet** in both places so the backend can act as treasury/compliance officer.

---

## Where the private key is used

| Location | File | Variable | Purpose |
|----------|------|----------|---------|
| **Contracts** | `contracts/.env` | `PRIVATE_KEY` | Deploy ComplianceRegistry and AegisFlowVault to Neon EVM |
| **Backend** | `backend/.env` | `PRIVATE_KEY` | Sign transactions (whitelist, limits, transfers) as treasury/AI agent |

**Webapp** does **not** use a private key; it talks to the backend API only.

---

## Which key to use (Somnia, Ethereum, etc. — same key)

**The private key is the same for every network.** In MetaMask, one account has one private key. It does **not** depend on which chain you have selected (Somnia, Ethereum, etc.). So:

- You **do not** need a “Solana” network in MetaMask for this project. AegisFlow uses **Neon EVM**, which is Ethereum-compatible (EVM).
- If you use MetaMask with **Somnia** (or any other EVM chain), the **same** private key from that account works for Neon EVM. Copy that key.
- **Which key to copy:** Export the private key from the **account you want to use** (e.g. the one you use on Somnia). That single key is used for all EVM chains, including Neon EVM. There is no separate “key per network.”

---

## How to get your private key from MetaMask

1. Open **MetaMask** and unlock it.
2. Select **any** network (e.g. Somnia or Ethereum Mainnet)—the key is the same for all.
3. Click the **three dots (⋮)** next to your **account name** (not the network).
4. Click **Account details**.
5. Click **Show private key** (or **Export Private Key**).
6. Enter your MetaMask password and confirm.
7. **Copy** the long hex string (64 characters, with or without the `0x` at the start). Use this **same** key in `contracts/.env` and `backend/.env`.

**Security:** Never share this key, never commit it to git, and never paste it in public. Anyone with this key controls the wallet.

---

## What to paste in `.env`

- In **contracts/.env** and **backend/.env**, set:
  ```env
  PRIVATE_KEY=paste_your_64_character_hex_here
  ```
- You can include or omit the leading `0x`; both work.

Use the **same** private key in both `contracts/.env` and `backend/.env` so the backend wallet is the same as the deployer (and thus has the right roles on-chain).

---

## Neon EVM setup (so the wallet can pay gas)

You do **not** need Solana in MetaMask. Add **Neon EVM Devnet** as a new network (it is EVM, like Somnia):

1. **Add Neon Devnet to MetaMask**
   - Network name: `Neon EVM Devnet`
   - RPC URL: `https://devnet.neonevm.org`
   - Chain ID: `245022926`
   - Symbol: `NEON`

2. **Get test NEON**
   - Go to [Neon Faucet](https://neonfaucet.org).
   - Enter your MetaMask address (same account whose private key you use).
   - Request test NEON so the wallet has gas for deployment and transactions.

3. **Deploy contracts** from the `contracts/` folder (see main README). After deployment, copy the contract addresses from `contracts/deployed.json` into **backend/.env** as `COMPLIANCE_REGISTRY_ADDRESS` and `AEGISFLOW_VAULT_ADDRESS`.

---

## Summary

- **One MetaMask account** → export its **private key**.
- Put that key in **contracts/.env** and **backend/.env** as `PRIVATE_KEY`.
- Add **Neon EVM Devnet** in MetaMask and get **test NEON** from the faucet.
- After deploying, fill **backend/.env** with the contract addresses from **contracts/deployed.json**.
