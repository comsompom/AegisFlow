"""Audit log for proposals and transactions."""
from datetime import datetime
from typing import Any

_audit_log: list[dict[str, Any]] = []


def log(
    action: str,
    actor: str,
    amount: int | None = None,
    counterparty: str | None = None,
    status: str = "success",
    tx_hash: str | None = None,
    reason: str | None = None,
    metadata: dict | None = None,
) -> None:
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "action": action,
        "actor": actor,
        "amount": amount,
        "counterparty": counterparty,
        "status": status,
        "tx_hash": tx_hash,
        "reason": reason,
        "metadata": metadata or {},
    }
    _audit_log.append(entry)


def get_log(limit: int = 100, action_filter: str | None = None) -> list[dict[str, Any]]:
    out = list(_audit_log)
    if action_filter:
        out = [e for e in out if e["action"] == action_filter]
    out.reverse()
    return out[:limit]
