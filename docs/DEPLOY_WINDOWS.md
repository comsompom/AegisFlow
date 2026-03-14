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
   Then install Anchor. **Prefer AVM** (avoids broken 0.30.1 cargo install):
   ```bash
   cargo install --git https://github.com/coral-xyz/anchor avm --force
   avm install latest
   avm use latest
   ```
   If you need 0.30.x specifically, try: `cargo install --git https://github.com/coral-xyz/anchor --tag v0.30.1 anchor-cli` (without `--locked`).

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

## Build fix (program ID and overflow-checks)

If `anchor build` fails with **"String is the wrong size"**: use a program ID that is **44 characters** (e.g. `AegisF1ow11111111111111111111111111111111111`) in `Anchor.toml` and in `programs/aegisflow/src/lib.rs` `declare_id!(...)`.

If it fails with **"overflow-checks is not enabled"**: add to the workspace root `Cargo.toml` (e.g. `contracts-solana/Cargo.toml`):
```toml
[profile.release]
overflow-checks = true
```

**"no such command: build-sbf"**: Anchor needs the Solana build toolchain. Either install the full **Solana CLI** (see below), or run `cargo install solana-cargo-build-sbf`, **close and reopen your terminal**, then run `anchor build` again. You still need the **Solana CLI** for `anchor deploy` (keypair, config, airdrop).

**"Failed to install platform-tools: A required privilege is not held by the client. (os error 1314)"**: On native Windows, `cargo-build-sbf` may need to create symlinks and can fail without admin rights. **Use WSL (Option A)** and run the deploy from Ubuntu, or run your terminal/PowerShell **as Administrator** and retry.

---

## Option B: Native Windows (Rust + VS Build Tools)

1. **Install Visual Studio 2022 Build Tools with C++** (required for Rust linker on Windows).  
   Run **PowerShell as Administrator**:
   ```powershell
   winget install Microsoft.VisualStudio.2022.BuildTools --override "--passive --wait --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"
   ```
   Close and reopen your terminal after install.

2. **Install Anchor CLI** (Rust + VS Build Tools already installed).  
   Option 2a — **without --locked** (often fixes "failed to compile" with 0.30.1):
   ```powershell
   cargo install --git https://github.com/coral-xyz/anchor --tag v0.30.1 anchor-cli
   ```
   Option 2b — **use AVM** (install latest Anchor; then use a matching program version if needed):
   ```powershell
   cargo install --git https://github.com/coral-xyz/anchor avm --force
   avm install latest
   avm use latest
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

## Troubleshooting

**"failed to compile anchor-cli v0.30.1" / anchor-syn warnings**  
- Install **without** `--locked` so Cargo can use non-yanked dependency versions:
  ```powershell
  cargo install --git https://github.com/coral-xyz/anchor --tag v0.30.1 anchor-cli
  ```
- If the build still fails at the end (e.g. only warnings from `anchor-syn` / `anchor-lang`), **allow warnings** so the install can complete:
  ```powershell
  $env:RUSTFLAGS="-A warnings"
  cargo install --git https://github.com/coral-xyz/anchor --tag v0.30.1 anchor-cli
  ```
- Or use **AVM** and latest Anchor (Option 2b above); if the program was written for 0.30.x, it usually still builds with a newer CLI.
- On Windows, ensure **Visual Studio 2022 Build Tools** with the **C++ workload** is installed so `link.exe` is available.

---

## After deploy (any option)

1. **backend\.env**: `SOLANA_PROGRAM_ID=<from anchor keys list>`, `SOLANA_KEYPAIR_PATH` or `SOLANA_PRIVATE_KEY` set.
2. **Initialize once**: `cd backend && python -m scripts.init_solana_program`
3. **Start backend**: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
4. **Start webapp**: `cd webapp && flask run` → http://localhost:5000
