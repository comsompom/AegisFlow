#!/usr/bin/env bash
# Deploy AegisFlow to Solana Devnet (run from WSL/Ubuntu).
# Prereqs: Solana CLI + Anchor CLI (e.g. via: curl ... solana-install ... | bash).
set -e
cd "$(dirname "$0")/.."
echo "=== AegisFlow Solana Devnet deploy ==="
command -v solana >/dev/null || { echo "Solana CLI not found. Install: https://docs.solana.com/cli/install"; exit 1; }
command -v anchor >/dev/null || { echo "Anchor CLI not found."; exit 1; }
echo "Solana: $(solana --version)"
echo "Anchor: $(anchor --version)"
cd contracts-solana
solana config set --url devnet
solana airdrop 2 || true
echo "Building..."
anchor build
PROGRAM_ID=$(anchor keys list 2>/dev/null | awk '{print $NF}')
[ -n "$PROGRAM_ID" ] && echo "Program ID: $PROGRAM_ID"
echo "Deploying..."
anchor deploy --provider.cluster devnet
echo ""
echo "Done. Set SOLANA_PROGRAM_ID=$PROGRAM_ID in backend/.env"
echo "Then: cd backend && python -m scripts.init_solana_program"
