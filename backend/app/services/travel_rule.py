"""Travel Rule payload generation and storage (keyed by tx hash)."""
import json
import uuid
from datetime import datetime
from typing import Any

# In-memory store for MVP; replace with DB (e.g. SQLAlchemy) for production
_travel_rule_store: dict[str, dict[str, Any]] = {}


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


def store_for_tx(tx_hash: str, payload: dict[str, Any]) -> None:
    _travel_rule_store[tx_hash.lower()] = payload


def get_by_tx_hash(tx_hash: str) -> dict[str, Any] | None:
    return _travel_rule_store.get(tx_hash.lower())


def list_all() -> list[dict[str, Any]]:
    return list(_travel_rule_store.values())
