"""Travel Rule payload generation and storage — persisted in SQLite."""
import json
from typing import Any
import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.models_db import TravelRulePayload


def create_payload(
    originator_name: str,
    originator_account: str,
    beneficiary_name: str,
    beneficiary_account: str,
    amount: float,
    vasp_originator_id: str = "",
    vasp_beneficiary_id: str = "",
) -> dict[str, Any]:
    payload = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "originator": {"name": originator_name, "account": originator_account},
        "beneficiary": {"name": beneficiary_name, "account": beneficiary_account},
        "amount": amount,
        "vasp_originator_id": vasp_originator_id,
        "vasp_beneficiary_id": vasp_beneficiary_id,
    }
    return payload


def store_for_tx(db: Session, tx_hash: str, payload: dict[str, Any]) -> None:
    key = tx_hash.lower()
    existing = db.query(TravelRulePayload).filter(TravelRulePayload.tx_hash == key).first()
    if existing:
        existing.payload_json = json.dumps(payload)
    else:
        row = TravelRulePayload(tx_hash=key, payload_json=json.dumps(payload))
        db.add(row)


def get_by_tx_hash(db: Session, tx_hash: str) -> dict[str, Any] | None:
    row = db.query(TravelRulePayload).filter(TravelRulePayload.tx_hash == tx_hash.lower()).first()
    if not row:
        return None
    return json.loads(row.payload_json)


def list_all(db: Session) -> list[dict[str, Any]]:
    rows = db.query(TravelRulePayload).order_by(TravelRulePayload.id.desc()).all()
    return [json.loads(r.payload_json) for r in rows]
