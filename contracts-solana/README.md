# AegisFlow — Native Solana (Anchor) Program

Compliance registry program for **Solana Devnet**. No Neon — uses Solana's native RPC and tooling.

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
# Update declare_id! in programs/aegisflow/src/lib.rs if needed, then:
anchor keys sync
anchor build
```

## Deploy to Solana Devnet

1. **Set CLI to Devnet and fund wallet**
   ```bash
   solana config set --url devnet
   solana airdrop 2
   ```

2. **Deploy**
   ```bash
   anchor deploy --provider.cluster devnet
   ```

3. **Note the program ID** from the deploy output (or `anchor keys list`). You will need it in the backend as `SOLANA_PROGRAM_ID` and the **ComplianceConfig PDA** (seeds: `["compliance"]`) for reading state.

## Program instructions

- `init_config(max_per_tx, max_daily_volume)` — init compliance config (authority = signer).
- `add_to_whitelist(address)` — compliance officer adds pubkey.
- `remove_from_whitelist(address)` — compliance officer removes.
- `add_to_blacklist(address)` — compliance officer blacklists.
- `set_limits(max_per_tx, max_daily_volume)` — owner only.
- `set_vault(vault_pubkey)` — owner only.
- `set_paused(paused)` — owner only.
- `record_volume(amount)` — vault/ai_agent/owner (for daily volume tracking).

## Backend integration

To use this program instead of Neon:

1. Set in backend `.env`: `USE_SOLANA_NATIVE=true`, `SOLANA_RPC_URL=https://api.devnet.solana.com`, `SOLANA_PROGRAM_ID=<your-program-id>`, and your Solana keypair path or base58 secret.
2. Backend must call the program via **anchorpy** or **solana-py** (read config account, send transactions for whitelist/limits). The current backend is wired for Neon (web3); a separate adapter or config switch is needed to use this Solana program.

See [SOLANA_VS_NEON.md](../docs/SOLANA_VS_NEON.md) for why we have both Neon and native Solana options.
