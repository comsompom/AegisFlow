from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.audit import log

router = APIRouter()

# In-memory agent state for MVP
_agent_status = {"running": False, "last_run": None}
_proposals: list[dict] = []


class Proposal(BaseModel):
    action: str  # transfer | swap
    amount: str
    recipient: str | None = None
    from_token: str | None = None
    to_token: str | None = None
    reason: str | None = None


@router.get("/status")
def agent_status():
    return _agent_status


@router.post("/status")
def set_agent_status(running: bool):
    _agent_status["running"] = running
    return _agent_status


@router.get("/proposals")
def list_proposals(limit: int = 50):
    return {"proposals": _proposals[-limit:][::-1]}


@router.post("/propose")
def submit_proposal(p: Proposal, db: Session = Depends(get_db)):
    """AI agent or user submits a proposal; compliance checks happen on execute."""
    entry = {
        "action": p.action,
        "amount": p.amount,
        "recipient": p.recipient,
        "from_token": p.from_token,
        "to_token": p.to_token,
        "reason": p.reason,
        "status": "pending",
    }
    _proposals.append(entry)
    log(db, "proposal", "ai_agent", metadata=entry)
    return {"ok": True, "proposal": entry}


@router.post("/run-once")
def run_agent_once():
    """Trigger one AI agent run (mock)."""
    from app.agents.treasury_agent import run_once
    try:
        result = run_once()
        _agent_status["last_run"] = result.get("timestamp")
        for p in result.get("proposals", []):
            _proposals.append(p)
        return result
    except Exception as e:
        raise HTTPException(500, str(e))
