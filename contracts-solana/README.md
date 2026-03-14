# AegisFlow — Native Solana (Anchor) Program

Compliance registry and vault program for **Solana Devnet**. Built for the hackathon: **all projects must be built on Solana**.

## Prerequisites

- [Rust](https://rustup.rs/)
- [Solana CLI](https://docs.solana.com/cli/install)
- [Anchor CLI](https://www.anchor-lang.com/docs/installation) 0.30.x

## Build

```bash
cd contracts-solana
anchor build
```

After first build, sync program ID (optional):

```bash
anchor keys list
anchor keys sync
anchor build
```

## Deploy to Solana Devnet

```bash
solana config set --url devnet
solana airdrop 2
anchor deploy --provider.cluster devnet
```

Note the **program ID** (from deploy output or `anchor keys list`) and set **SOLANA_PROGRAM_ID** in backend `.env`.

## Initialize (after first deploy)

The config and vault accounts must be created once:

1. **init_config(max_per_tx, max_daily_volume)** — creates the ComplianceConfig PDA. Call with e.g. `max_per_tx = 1_000_000_000`, `max_daily_volume = 10_000_000_000` (lamports).
2. **init_vault()** — creates the vault PDA (so it can hold SOL).
3. **set_vault(vault_pda)** — sets the vault pubkey in config (use the vault PDA address from step 2).

You can call these from the Anchor TypeScript tests, or from a small script using the Anchor TS client. The backend does not call `init_config`; it expects the program to be already initialized.

## Program instructions

- **init_config(max_per_tx, max_daily_volume)** — init compliance config (authority = signer). Call once.
- **init_vault()** — create vault PDA. Call once.
- **add_to_whitelist(address)** — compliance officer adds pubkey.
- **remove_from_whitelist(address)** — compliance officer removes.
- **add_to_blacklist(address)** — compliance officer blacklists.
- **set_limits(max_per_tx, max_daily_volume)** — owner only.
- **set_vault(vault_pubkey)** — owner only (set after init_vault).
- **set_paused(paused)** — owner only.
- **record_volume(amount)** — vault/ai_agent/owner (used internally by vault_withdraw).
- **vault_withdraw(amount)** — transfer SOL from vault PDA to whitelisted recipient (accounts: config, vault, recipient, authority, system_program).

## Backend

The backend is **Solana-only**. Set in backend `.env`:

- **SOLANA_RPC_URL** — e.g. `https://api.devnet.solana.com`
- **SOLANA_PROGRAM_ID** — program ID from `anchor keys list`
- **SOLANA_KEYPAIR_PATH** or **SOLANA_PRIVATE_KEY** — signer for whitelist/limits/vault_withdraw

The backend reads the ComplianceConfig PDA (seeds: `["compliance"]`) and submits transactions for whitelist, limits, and vault_withdraw.
