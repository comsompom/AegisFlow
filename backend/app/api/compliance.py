from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.blockchain import get_registry_contract, get_limits
from web3 import Web3

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


@router.get("/whitelist/{address}")
def check_whitelist(address: str):
    from app.services.blockchain import is_whitelisted
    return {"address": address, "whitelisted": is_whitelisted(address)}


@router.get("/limits")
def limits():
    return get_limits()


@router.post("/whitelist")
def add_to_whitelist(body: WhitelistAdd):
    contract = get_registry_contract()
    if not contract:
        raise HTTPException(503, "Contract not configured")
    try:
        addr = Web3.to_checksum_address(body.address)
        tx = contract.functions.addToWhitelist(addr)
        # In production: build, sign, send via backend wallet
        return {"ok": True, "message": "Would submit tx (configure backend signer)"}
    except Exception as e:
        raise HTTPException(400, str(e))


@router.delete("/whitelist")
def remove_from_whitelist(body: WhitelistRemove):
    contract = get_registry_contract()
    if not contract:
        raise HTTPException(503, "Contract not configured")
    try:
        addr = Web3.to_checksum_address(body.address)
        contract.functions.removeFromWhitelist(addr)
        return {"ok": True, "message": "Would submit tx"}
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/blacklist")
def add_to_blacklist(body: BlacklistAdd):
    contract = get_registry_contract()
    if not contract:
        raise HTTPException(503, "Contract not configured")
    try:
        addr = Web3.to_checksum_address(body.address)
        contract.functions.addToBlacklist(addr)
        return {"ok": True, "message": "Would submit tx"}
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/limits")
def update_limits(body: LimitsUpdate):
    contract = get_registry_contract()
    if not contract:
        raise HTTPException(503, "Contract not configured")
    try:
        max_per_tx = int(body.max_per_tx)
        max_daily = int(body.max_daily_volume)
        contract.functions.setLimits(max_per_tx, max_daily)
        return {"ok": True, "message": "Would submit tx"}
    except Exception as e:
        raise HTTPException(400, str(e))
