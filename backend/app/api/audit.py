from fastapi import APIRouter
from app.services.audit import get_log
from app.services.travel_rule import get_by_tx_hash, list_all as travel_list

router = APIRouter()


@router.get("/log")
def audit_log(limit: int = 100, action: str | None = None):
    return {"entries": get_log(limit=limit, action_filter=action)}


@router.get("/travel-rule/{tx_hash}")
def travel_rule_by_tx(tx_hash: str):
    payload = get_by_tx_hash(tx_hash)
    if not payload:
        return {"found": False, "payload": None}
    return {"found": True, "payload": payload}


@router.get("/travel-rule")
def travel_rule_list():
    return {"payloads": travel_list()}
