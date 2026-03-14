#!/usr/bin/env python3
"""
Deploy AegisFlow contracts (ComplianceRegistry, AegisFlowVault) to Neon EVM using Python.
Usage (from contracts/ directory):
    python deploy.py
Requires: .env with PRIVATE_KEY and optionally NEON_RPC_URL.
"""
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Default limits (18 decimals): 1M per tx, 10M daily
DEFAULT_MAX_PER_TX = 1_000_000 * 10**18
DEFAULT_MAX_DAILY = 10_000_000 * 10**18


def _ensure_solc():
    try:
        import solcx
    except ImportError:
        print("Install solcx: pip install solcx", file=sys.stderr)
        sys.exit(1)
    if not hasattr(solcx, "install_solc") or not callable(getattr(solcx, "install_solc", None)):
        # solcx 0.2+ uses install_solc
        pass
    try:
        solcx.install_solc("0.8.20")
    except Exception as e:
        print(f"solcx install_solc: {e}", file=sys.stderr)
        sys.exit(1)


def compile_contracts(contracts_dir: Path):
    import solcx
    solcx.install_solc("0.8.20")
    registry_path = contracts_dir / "ComplianceRegistry.sol"
    vault_path = contracts_dir / "AegisFlowVault.sol"
    if not registry_path.exists() or not vault_path.exists():
        print(f"Contracts not found in {contracts_dir}", file=sys.stderr)
        sys.exit(1)
    compiled = solcx.compile_files(
        [str(registry_path), str(vault_path)],
        output_values=["abi", "bin"],
        solc_version="0.8.20",
        import_remappings=[],
    )
    # Keys are like "ComplianceRegistry.sol:ComplianceRegistry" or "contracts/ComplianceRegistry.sol:ComplianceRegistry"
    all_keys = list(compiled.keys())
    registry_key = next((k for k in all_keys if k.split(":")[-1] == "ComplianceRegistry"), None)
    vault_key = next((k for k in all_keys if k.split(":")[-1] == "AegisFlowVault"), None)
    if not registry_key or not vault_key:
        print("Compiled keys:", all_keys, file=sys.stderr)
        sys.exit(1)
    return {
        "ComplianceRegistry": compiled[registry_key],
        "AegisFlowVault": compiled[vault_key],
    }


def deploy():
    from web3 import Web3

    script_dir = Path(__file__).resolve().parent
    contracts_dir = script_dir / "contracts"
    rpc_url = os.environ.get("NEON_RPC_URL", "https://devnet.neonevm.org")
    private_key = os.environ.get("PRIVATE_KEY", "").strip()
    if not private_key:
        print("Set PRIVATE_KEY in .env", file=sys.stderr)
        sys.exit(1)
    if private_key.startswith("0x"):
        private_key = private_key[2:]

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        print(f"Cannot connect to {rpc_url}", file=sys.stderr)
        sys.exit(1)

    account = w3.eth.account.from_key(private_key)
    deployer = account.address
    print(f"Deployer: {deployer}")
    balance = w3.eth.get_balance(deployer)
    print(f"Balance: {balance} wei")

    print("Compiling contracts...")
    compiled = compile_contracts(contracts_dir)

    def _bin(key):
        b = compiled[key]["bin"] or ""
        return b if (isinstance(b, str) and b.startswith("0x")) else "0x" + b

    registry_abi = compiled["ComplianceRegistry"]["abi"]
    registry_bin = _bin("ComplianceRegistry")
    vault_abi = compiled["AegisFlowVault"]["abi"]
    vault_bin = _bin("AegisFlowVault")

    # 1. Deploy ComplianceRegistry
    print("Deploying ComplianceRegistry...")
    Registry = w3.eth.contract(abi=registry_abi, bytecode=registry_bin)
    tx = Registry.constructor(
        deployer,  # complianceOfficer
        deployer,  # aiAgent
        DEFAULT_MAX_PER_TX,
        DEFAULT_MAX_DAILY,
    ).build_transaction(
        {
            "from": deployer,
            "nonce": w3.eth.get_transaction_count(deployer),
            "gas": 5_000_000,
        }
    )
    signed = w3.eth.account.sign_transaction(tx, account.key)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    registry_address = receipt["contractAddress"]
    print(f"ComplianceRegistry: {registry_address}")

    # 2. Deploy AegisFlowVault
    print("Deploying AegisFlowVault...")
    Vault = w3.eth.contract(abi=vault_abi, bytecode=vault_bin)
    tx2 = Vault.constructor(registry_address, deployer).build_transaction(
        {
            "from": deployer,
            "nonce": w3.eth.get_transaction_count(deployer),
            "gas": 5_000_000,
        }
    )
    signed2 = w3.eth.account.sign_transaction(tx2, account.key)
    tx_hash2 = w3.eth.send_raw_transaction(signed2.raw_transaction)
    receipt2 = w3.eth.wait_for_transaction_receipt(tx_hash2)
    vault_address = receipt2["contractAddress"]
    print(f"AegisFlowVault: {vault_address}")

    # 3. Set vault in registry
    print("Setting vault in ComplianceRegistry...")
    registry = w3.eth.contract(address=Web3.to_checksum_address(registry_address), abi=registry_abi)
    tx3 = registry.functions.setVault(Web3.to_checksum_address(vault_address)).build_transaction(
        {
            "from": deployer,
            "nonce": w3.eth.get_transaction_count(deployer),
            "gas": 200_000,
        }
    )
    signed3 = w3.eth.account.sign_transaction(tx3, account.key)
    tx_hash3 = w3.eth.send_raw_transaction(signed3.raw_transaction)
    w3.eth.wait_for_transaction_receipt(tx_hash3)

    chain_id = w3.eth.chain_id
    output = {
        "network": "neon_devnet",
        "chainId": str(chain_id),
        "deployer": deployer,
        "contracts": {
            "ComplianceRegistry": registry_address,
            "AegisFlowVault": vault_address,
        },
    }
    out_path = script_dir / "deployed.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Wrote {out_path}")
    return output


if __name__ == "__main__":
    _ensure_solc()
    deploy()
