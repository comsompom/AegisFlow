from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.audit import get_log
from app.services.travel_rule import get_by_tx_hash, list_all as travel_list

router = APIRouter()


@router.get("/log")
def audit_log(limit: int = 100, action: str | None = None, db: Session = Depends(get_db)):
    return {"entries": get_log(db, limit=limit, action_filter=action)}


@router.get("/travel-rule/{tx_hash}")
def travel_rule_by_tx(tx_hash: str, db: Session = Depends(get_db)):
    payload = get_by_tx_hash(db, tx_hash)
    if not payload:
        return {"found": False, "payload": None}
    return {"found": True, "payload": payload}


@router.get("/travel-rule")
def travel_rule_list(db: Session = Depends(get_db)):
    return {"payloads": travel_list(db)}
