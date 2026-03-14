from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.config import get_settings
from app.services.blockchain import get_limits, is_whitelisted
from app.services import blockchain_solana

router = APIRouter()


class WhitelistAdd(BaseModel):
    address: str


class WhitelistRemove(BaseModel):
    address: str


class BlacklistAdd(BaseModel):
    address: str


class LimitsUpdate(BaseModel):
    max_per_tx: str
    max_daily_volume: str


def _require_solana():
    if not get_settings().solana_program_id:
        raise HTTPException(503, "Solana program not configured (set SOLANA_PROGRAM_ID)")


@router.get("/whitelist/{address}")
def check_whitelist(address: str):
    return {"address": address, "whitelisted": is_whitelisted(address)}


@router.get("/limits")
def limits():
    return get_limits()


@router.post("/whitelist")
def add_to_whitelist(body: WhitelistAdd):
    _require_solana()
    try:
        sig = blockchain_solana.add_to_whitelist(body.address)
        if sig:
            return {"ok": True, "message": "Transaction submitted", "signature": sig}
        return {"ok": False, "message": "Submit failed (check keypair and RPC)"}
    except Exception as e:
        raise HTTPException(400, str(e))


@router.delete("/whitelist")
def remove_from_whitelist(body: WhitelistRemove):
    _require_solana()
    try:
        sig = blockchain_solana.remove_from_whitelist(body.address)
        if sig:
            return {"ok": True, "message": "Transaction submitted", "signature": sig}
        return {"ok": False, "message": "Submit failed (check keypair and RPC)"}
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/blacklist")
def add_to_blacklist(body: BlacklistAdd):
    _require_solana()
    try:
        sig = blockchain_solana.add_to_blacklist(body.address)
        if sig:
            return {"ok": True, "message": "Transaction submitted", "signature": sig}
        return {"ok": False, "message": "Submit failed (check keypair and RPC)"}
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/limits")
def update_limits(body: LimitsUpdate):
    _require_solana()
    try:
        max_per_tx = int(body.max_per_tx)
        max_daily = int(body.max_daily_volume)
        sig = blockchain_solana.set_limits(max_per_tx, max_daily)
        if sig:
            return {"ok": True, "message": "Transaction submitted", "signature": sig}
        return {"ok": False, "message": "Submit failed (check keypair and RPC)"}
    except Exception as e:
        raise HTTPException(400, str(e))
