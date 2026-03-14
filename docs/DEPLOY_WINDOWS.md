# Deploy AegisFlow on Windows (Solana Devnet)

To deploy the Anchor program from Windows you need **Solana CLI** and **Anchor CLI**. Two options:

---

## Option A: WSL (Ubuntu) — recommended

1. **Install Ubuntu in WSL** (if not already):
   ```powershell
   wsl --install -d Ubuntu
   ```
   Restart if prompted, then open **Ubuntu** from the Start menu.

2. **In the Ubuntu terminal**, run the one-line Solana + Anchor install:
   ```bash
   sh -c "$(curl -sSfL https://release.anza.xyz/stable/install)"
   ```
   Then install Anchor (e.g. via AVM):
   ```bash
   cargo install --git https://github.com/coral-xyz/anchor avm --locked --force
   avm install latest
   avm use latest
   ```
   Or follow the official [Anchor installation](https://www.anchor-lang.com/docs/installation) for Linux.

3. **Clone or open the repo in WSL** (e.g. project under `~/AegisFlow` or `/mnt/c/Users/obourdo/AegisFlow`).

4. **Deploy from Ubuntu**:
   ```bash
   cd /mnt/c/Users/obourdo/AegisFlow/contracts-solana
   solana config set --url devnet
   solana airdrop 2
   anchor build
   anchor keys list    # copy the program ID
   anchor deploy --provider.cluster devnet
   ```

5. **Copy the program ID** into `backend\.env` as `SOLANA_PROGRAM_ID=...`.

6. **Initialize** (from Windows PowerShell, in the repo):
   ```powershell
   cd backend
   python -m scripts.init_solana_program
   ```

---

## Option B: Native Windows (Rust + VS Build Tools)

1. **Install Visual Studio 2022 Build Tools with C++** (required for Rust linker on Windows).  
   Run **PowerShell as Administrator**:
   ```powershell
   winget install Microsoft.VisualStudio.2022.BuildTools --override "--passive --wait --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"
   ```
   Close and reopen your terminal after install.

2. **Install Anchor CLI** (Rust is already installed):
   ```powershell
   cargo install --git https://github.com/coral-xyz/anchor --tag v0.30.1 anchor-cli --locked
   ```

3. **Install Solana CLI for Windows**:
   - Download: https://github.com/solana-labs/solana/releases (get `solana-release-x86_64-pc-windows-msvc.tar.bz2` or the Windows installer if available).
   - Or in WSL Ubuntu run the Anza install (step 2 in Option A), then use `solana` from WSL for deploy.

4. **Deploy** (if both `solana` and `anchor` are in PATH):
   ```powershell
   cd C:\Users\obourdo\AegisFlow
   .\scripts\deploy_solana_devnet.ps1
   ```

5. Set **SOLANA_PROGRAM_ID** in `backend\.env`, then run **init** (step 6 in Option A).

---

## After deploy (any option)

1. **backend\.env**: `SOLANA_PROGRAM_ID=<from anchor keys list>`, `SOLANA_KEYPAIR_PATH` or `SOLANA_PRIVATE_KEY` set.
2. **Initialize once**: `cd backend && python -m scripts.init_solana_program`
3. **Start backend**: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
4. **Start webapp**: `cd webapp && flask run` → http://localhost:5000
