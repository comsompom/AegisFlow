"""Solana (Anchor) client for AegisFlow compliance program. Used when building for Solana hackathon."""
import struct
import hashlib
import base64
import os
from typing import Optional

from app.config import get_settings

# Lazy imports to avoid requiring solana/solders when not used
_solana_client = None


def _get_rpc():
    from solana.rpc.api import Client
    s = get_settings()
    return Client(s.solana_rpc_url)


def _get_program_id():
    from solders.pubkey import Pubkey
    s = get_settings()
    return Pubkey.from_string(s.solana_program_id)


def _get_config_pda():
    from solders.pubkey import Pubkey
    program_id = _get_program_id()
    pda, _ = Pubkey.find_program_address([b"compliance"], program_id)
    return pda


def _get_vault_pda():
    from solders.pubkey import Pubkey
    program_id = _get_program_id()
    pda, _ = Pubkey.find_program_address([b"vault"], program_id)
    return pda


def _get_signer_keypair():
    """Load keypair from SOLANA_KEYPAIR_PATH (json file) or SOLANA_PRIVATE_KEY (base58)."""
    from solders.keypair import Keypair
    s = get_settings()
    if s.solana_keypair_path and os.path.isfile(s.solana_keypair_path):
        with open(s.solana_keypair_path) as f:
            import json
            data = json.load(f)
            return Keypair.from_bytes(bytes(data))
    if s.solana_private_key:
        try:
            from solders.keypair import Keypair
            return Keypair.from_base58_string(s.solana_private_key)
        except Exception:
            pass
        try:
            raw = base64.b64decode(s.solana_private_key)
            if len(raw) == 64:
                return Keypair.from_bytes(raw)
        except Exception:
            pass
    return None


def _instruction_discriminator(name: str) -> bytes:
    h = hashlib.sha256(f"global:{name}".encode()).digest()
    return h[:8]


def _fetch_config_account() -> Optional[bytes]:
    rpc = _get_rpc()
    pda = _get_config_pda()
    resp = rpc.get_account_info(pda)
    if resp.value and resp.value.data:
        return bytes(resp.value.data)
    return None


def _parse_config(data: bytes) -> Optional[dict]:
    """Parse ComplianceConfig account (after 8-byte discriminator). Layout: 4*Pubkey, whitelist Vec<Pubkey>, blacklist Vec<Pubkey>, u64,u64,u64,i64,u8,u8."""
    if len(data) < 8 + 128:
        return None
    off = 8  # skip discriminator
    # 4 pubkeys
    authority = data[off:off + 32].hex()
    off += 32
    compliance_officer = data[off:off + 32].hex()
    off += 32
    ai_agent = data[off:off + 32].hex()
    off += 32
    vault = data[off:off + 32].hex()
    off += 32
    # whitelist: 4 bytes len (u32 LE) + 32*len
    wlen = struct.unpack_from("<I", data, off)[0]
    off += 4
    if off + wlen * 32 > len(data):
        return None
    whitelist = []
    for _ in range(wlen):
        whitelist.append(data[off:off + 32].hex())
        off += 32
    # blacklist
    blen = struct.unpack_from("<I", data, off)[0]
    off += 4
    if off + blen * 32 > len(data):
        return None
    blacklist = []
    for _ in range(blen):
        blacklist.append(data[off:off + 32].hex())
        off += 32
    if off + 8 + 8 + 8 + 8 + 1 + 1 > len(data):
        return None
    max_per_tx = struct.unpack_from("<Q", data, off)[0]
    off += 8
    max_daily_volume = struct.unpack_from("<Q", data, off)[0]
    off += 8
    daily_volume_used = struct.unpack_from("<Q", data, off)[0]
    off += 8
    daily_volume_reset_time = struct.unpack_from("<q", data, off)[0]
    off += 8
    paused = data[off]
    off += 1
    bump = data[off]
    return {
        "authority": authority,
        "compliance_officer": compliance_officer,
        "ai_agent": ai_agent,
        "vault": vault,
        "whitelist": whitelist,
        "blacklist": blacklist,
        "max_per_tx": max_per_tx,
        "max_daily_volume": max_daily_volume,
        "daily_volume_used": daily_volume_used,
        "daily_volume_reset_time": daily_volume_reset_time,
        "paused": bool(paused),
        "bump": bump,
    }


def _pubkey_hex_to_bytes(hex_str: str) -> bytes:
    """Convert Solana address (base58 or hex) to 32 bytes. If hex, decode; else decode base58 to 32 bytes."""
    if len(hex_str) == 64 and all(c in "0123456789abcdefABCDEF" for c in hex_str):
        return bytes.fromhex(hex_str)
    from solders.pubkey import Pubkey
    try:
        pk = Pubkey.from_string(hex_str)
        return bytes(pk)
    except Exception:
        return bytes(32)


def is_whitelisted(address: str) -> bool:
    data = _fetch_config_account()
    if not data:
        return False
    config = _parse_config(data)
    if not config:
        return False
    addr_bytes = _pubkey_hex_to_bytes(address)
    addr_hex = addr_bytes.hex()
    return addr_hex in config["whitelist"]


def get_limits() -> dict:
    data = _fetch_config_account()
    if not data:
        return {"maxPerTx": 0, "maxDailyVolume": 0, "dailyVolumeUsed": 0}
    config = _parse_config(data)
    if not config:
        return {"maxPerTx": 0, "maxDailyVolume": 0, "dailyVolumeUsed": 0}
    return {
        "maxPerTx": config["max_per_tx"],
        "maxDailyVolume": config["max_daily_volume"],
        "dailyVolumeUsed": config["daily_volume_used"],
    }


def get_balance(address: str) -> int:
    """Return vault PDA lamports (Solana: vault holds SOL). Ignore address for vault balance."""
    from solders.pubkey import Pubkey
    rpc = _get_rpc()
    vault_pda = _get_vault_pda()
    resp = rpc.get_account_info(vault_pda)
    if resp.value and resp.value.lamports is not None:
        return resp.value.lamports
    return 0


def add_to_whitelist(address: str) -> str | None:
    """Submit add_to_whitelist instruction. Returns tx signature or None on error."""
    from solders.instruction import Instruction, AccountMeta
    from solders.transaction import Transaction
    from solders.pubkey import Pubkey
    keypair = _get_signer_keypair()
    if not keypair:
        return None
    program_id = _get_program_id()
    config_pda = _get_config_pda()
    try:
        addr_pubkey = Pubkey.from_string(address)
    except Exception:
        addr_pubkey = Pubkey(_pubkey_hex_to_bytes(address))
    disc = _instruction_discriminator("add_to_whitelist")
    data = disc + bytes(addr_pubkey)
    ix = Instruction(
        program_id=program_id,
        data=data,
        accounts=[
            AccountMeta(pubkey=config_pda, is_signer=False, is_writable=True),
            AccountMeta(pubkey=keypair.pubkey(), is_signer=True, is_writable=False),
        ],
    )
    client = _get_rpc()
    recent = client.get_latest_blockhash()
    if not recent.value:
        return None
    msg = Transaction.new_with_payer([ix], keypair.pubkey())
    msg.recent_blockhash = recent.value
    msg.sign([keypair], msg.recent_blockhash)
    result = client.send_transaction(msg)
    if result.value:
        return str(result.value)
    return None


def remove_from_whitelist(address: str) -> str | None:
    from solders.instruction import Instruction, AccountMeta
    from solders.transaction import Transaction
    from solders.pubkey import Pubkey
    keypair = _get_signer_keypair()
    if not keypair:
        return None
    program_id = _get_program_id()
    config_pda = _get_config_pda()
    try:
        addr_pubkey = Pubkey.from_string(address)
    except Exception:
        addr_pubkey = Pubkey(_pubkey_hex_to_bytes(address))
    disc = _instruction_discriminator("remove_from_whitelist")
    data = disc + bytes(addr_pubkey)
    ix = Instruction(
        program_id=program_id,
        data=data,
        accounts=[
            AccountMeta(pubkey=config_pda, is_signer=False, is_writable=True),
            AccountMeta(pubkey=keypair.pubkey(), is_signer=True, is_writable=False),
        ],
    )
    client = _get_rpc()
    recent = client.get_latest_blockhash()
    if not recent.value:
        return None
    msg = Transaction.new_with_payer([ix], keypair.pubkey())
    msg.recent_blockhash = recent.value
    msg.sign([keypair], msg.recent_blockhash)
    result = client.send_transaction(msg)
    if result.value:
        return str(result.value)
    return None


def add_to_blacklist(address: str) -> str | None:
    from solders.instruction import Instruction, AccountMeta
    from solders.transaction import Transaction
    from solders.pubkey import Pubkey
    keypair = _get_signer_keypair()
    if not keypair:
        return None
    program_id = _get_program_id()
    config_pda = _get_config_pda()
    try:
        addr_pubkey = Pubkey.from_string(address)
    except Exception:
        addr_pubkey = Pubkey(_pubkey_hex_to_bytes(address))
    disc = _instruction_discriminator("add_to_blacklist")
    data = disc + bytes(addr_pubkey)
    ix = Instruction(
        program_id=program_id,
        data=data,
        accounts=[
            AccountMeta(pubkey=config_pda, is_signer=False, is_writable=True),
            AccountMeta(pubkey=keypair.pubkey(), is_signer=True, is_writable=False),
        ],
    )
    client = _get_rpc()
    recent = client.get_latest_blockhash()
    if not recent.value:
        return None
    msg = Transaction.new_with_payer([ix], keypair.pubkey())
    msg.recent_blockhash = recent.value
    msg.sign([keypair], msg.recent_blockhash)
    result = client.send_transaction(msg)
    if result.value:
        return str(result.value)
    return None


def set_limits(max_per_tx: int, max_daily_volume: int) -> str | None:
    from solders.instruction import Instruction, AccountMeta
    from solders.transaction import Transaction
    keypair = _get_signer_keypair()
    if not keypair:
        return None
    program_id = _get_program_id()
    config_pda = _get_config_pda()
    disc = _instruction_discriminator("set_limits")
    data = disc + struct.pack("<Q", max_per_tx) + struct.pack("<Q", max_daily_volume)
    ix = Instruction(
        program_id=program_id,
        data=data,
        accounts=[
            AccountMeta(pubkey=config_pda, is_signer=False, is_writable=True),
            AccountMeta(pubkey=keypair.pubkey(), is_signer=True, is_writable=False),
        ],
    )
    client = _get_rpc()
    recent = client.get_latest_blockhash()
    if not recent.value:
        return None
    msg = Transaction.new_with_payer([ix], keypair.pubkey())
    msg.recent_blockhash = recent.value
    msg.sign([keypair], msg.recent_blockhash)
    result = client.send_transaction(msg)
    if result.value:
        return str(result.value)
    return None


def vault_withdraw(recipient_address: str, lamports: int) -> str | None:
    """Execute vault_withdraw: transfer SOL from vault PDA to whitelisted recipient."""
    from solders.instruction import Instruction, AccountMeta
    from solders.transaction import Transaction
    from solders.pubkey import Pubkey
    from solders.system_program import ID as SYS_PROGRAM_ID
    keypair = _get_signer_keypair()
    if not keypair:
        return None
    program_id = _get_program_id()
    config_pda = _get_config_pda()
    vault_pda = _get_vault_pda()
    try:
        recipient = Pubkey.from_string(recipient_address)
    except Exception:
        recipient = Pubkey(_pubkey_hex_to_bytes(recipient_address))
    disc = _instruction_discriminator("vault_withdraw")
    data = disc + struct.pack("<Q", lamports)
    ix = Instruction(
        program_id=program_id,
        data=data,
        accounts=[
            AccountMeta(pubkey=config_pda, is_signer=False, is_writable=True),
            AccountMeta(pubkey=vault_pda, is_signer=False, is_writable=True),
            AccountMeta(pubkey=recipient, is_signer=False, is_writable=True),
            AccountMeta(pubkey=keypair.pubkey(), is_signer=True, is_writable=False),
            AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
        ],
    )
    client = _get_rpc()
    recent = client.get_latest_blockhash()
    if not recent.value:
        return None
    msg = Transaction.new_with_payer([ix], keypair.pubkey())
    msg.recent_blockhash = recent.value
    msg.sign([keypair], msg.recent_blockhash)
    result = client.send_transaction(msg)
    if result.value:
        return str(result.value)
    return None


# Placeholders for API compatibility (no registry/vault contracts on Solana)
def get_registry_contract():
    return "solana"  # sentinel


def get_vault_contract():
    return "solana"
