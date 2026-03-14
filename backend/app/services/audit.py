"""Audit log — persisted in SQLite."""
import json
from typing import Any

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models_db import AuditLog


def log(
    db: Session,
    action: str,
    actor: str,
    amount: int | None = None,
    counterparty: str | None = None,
    status: str = "success",
    tx_hash: str | None = None,
    reason: str | None = None,
    metadata: dict | None = None,
) -> None:
    entry = AuditLog(
        action=action,
        actor=actor,
        amount=amount,
        counterparty=counterparty,
        status=status,
        tx_hash=tx_hash,
        reason=reason,
        metadata_json=json.dumps(metadata) if metadata else None,
    )
    db.add(entry)


def get_log(db: Session, limit: int = 100, action_filter: str | None = None) -> list[dict[str, Any]]:
    q = db.query(AuditLog).order_by(desc(AuditLog.id))
    if action_filter:
        q = q.filter(AuditLog.action == action_filter)
    rows = q.limit(limit).all()
    return [
        {
            "timestamp": r.timestamp.isoformat() + "Z" if r.timestamp else None,
            "action": r.action,
            "actor": r.actor,
            "amount": r.amount,
            "counterparty": r.counterparty,
            "status": r.status,
            "tx_hash": r.tx_hash,
            "reason": r.reason,
            "metadata": json.loads(r.metadata_json) if r.metadata_json else {},
        }
        for r in rows
    ]
