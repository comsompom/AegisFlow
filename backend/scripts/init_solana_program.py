"""
One-time script to initialize the AegisFlow program on Solana Devnet.
Run from backend dir with .env set (SOLANA_RPC_URL, SOLANA_PROGRAM_ID, SOLANA_KEYPAIR_PATH or SOLANA_PRIVATE_KEY).

  python -m scripts.init_solana_program
"""
import struct
import hashlib
import os
import sys

# Add parent so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()


def _disc(name: str) -> bytes:
    return hashlib.sha256(f"global:{name}".encode()).digest()[:8]


def main():
    from solders.pubkey import Pubkey
    from solders.instruction import Instruction, AccountMeta
    from solders.transaction import Transaction
    from solders.system_program import ID as SYS_ID
    from solana.rpc.api import Client

    rpc_url = os.environ.get("SOLANA_RPC_URL", "https://api.devnet.solana.com")
    program_id_str = os.environ.get("SOLANA_PROGRAM_ID")
    if not program_id_str:
        print("Set SOLANA_PROGRAM_ID in .env")
        sys.exit(1)
    program_id = Pubkey.from_string(program_id_str)

    # Keypair
    keypair_path = os.environ.get("SOLANA_KEYPAIR_PATH")
    if keypair_path and os.path.isfile(os.path.expanduser(keypair_path)):
        import json
        with open(os.path.expanduser(keypair_path)) as f:
            keypair = __import__("solders.keypair", fromlist=["Keypair"]).Keypair.from_bytes(bytes(json.load(f)))
    elif os.environ.get("SOLANA_PRIVATE_KEY"):
        keypair = __import__("solders.keypair", fromlist=["Keypair"]).Keypair.from_base58_string(os.environ["SOLANA_PRIVATE_KEY"])
    else:
        print("Set SOLANA_KEYPAIR_PATH or SOLANA_PRIVATE_KEY in .env")
        sys.exit(1)

    client = Client(rpc_url)
    config_pda, _ = Pubkey.find_program_address([b"compliance"], program_id)
    vault_pda, _ = Pubkey.find_program_address([b"vault"], program_id)

    # init_config(max_per_tx, max_daily_volume)
    max_per_tx = 1_000_000_000  # 1 SOL in lamports
    max_daily_volume = 10_000_000_000  # 10 SOL
    data_init_config = _disc("init_config") + struct.pack("<QQ", max_per_tx, max_daily_volume)
    ix_init_config = Instruction(
        program_id=program_id,
        data=data_init_config,
        accounts=[
            AccountMeta(pubkey=config_pda, is_signer=False, is_writable=True),
            AccountMeta(pubkey=keypair.pubkey(), is_signer=True, is_writable=True),
            AccountMeta(pubkey=SYS_ID, is_signer=False, is_writable=False),
        ],
    )

    # init_vault() — vault account space 8+1, seeds [b"vault"]
    # Anchor init needs: vault (init, PDA), authority (signer), system_program
    data_init_vault = _disc("init_vault")
    ix_init_vault = Instruction(
        program_id=program_id,
        data=data_init_vault,
        accounts=[
            AccountMeta(pubkey=vault_pda, is_signer=False, is_writable=True),
            AccountMeta(pubkey=keypair.pubkey(), is_signer=True, is_writable=True),
            AccountMeta(pubkey=SYS_ID, is_signer=False, is_writable=False),
        ],
    )

    # set_vault(vault_pda)
    data_set_vault = _disc("set_vault") + bytes(vault_pda)
    ix_set_vault = Instruction(
        program_id=program_id,
        data=data_set_vault,
        accounts=[
            AccountMeta(pubkey=config_pda, is_signer=False, is_writable=True),
            AccountMeta(pubkey=keypair.pubkey(), is_signer=True, is_writable=False),
        ],
    )

    # Send init_config
    print("Sending init_config...")
    recent = client.get_latest_blockhash()
    if not recent.value:
        print("Failed to get blockhash")
        sys.exit(1)
    tx = Transaction.new_with_payer([ix_init_config], keypair.pubkey())
    tx.recent_blockhash = recent.value
    tx.sign([keypair], recent.value)
    r = client.send_transaction(tx)
    if r.value:
        print("  init_config tx:", r.value)
    else:
        print("  init_config failed:", r)
        sys.exit(1)

    # Send init_vault
    print("Sending init_vault...")
    recent = client.get_latest_blockhash()
    tx2 = Transaction.new_with_payer([ix_init_vault], keypair.pubkey())
    tx2.recent_blockhash = recent.value
    tx2.sign([keypair], recent.value)
    r2 = client.send_transaction(tx2)
    if r2.value:
        print("  init_vault tx:", r2.value)
    else:
        print("  init_vault failed:", r2)
        sys.exit(1)

    # Send set_vault
    print("Sending set_vault...")
    recent = client.get_latest_blockhash()
    tx3 = Transaction.new_with_payer([ix_set_vault], keypair.pubkey())
    tx3.recent_blockhash = recent.value
    tx3.sign([keypair], recent.value)
    r3 = client.send_transaction(tx3)
    if r3.value:
        print("  set_vault tx:", r3.value)
    else:
        print("  set_vault failed:", r3)
        sys.exit(1)

    print("Done. Config and vault initialized.")


if __name__ == "__main__":
    main()
