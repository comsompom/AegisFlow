from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.services.compliance import check_kyc, check_aml, run_compliance_checks
from app.services.travel_rule import create_payload, store_for_tx
from app.services.audit import log

router = APIRouter()


class TransferRequest(BaseModel):
    from_address: str
    to_address: str
    amount: str  # wei or raw units
    originator_name: str | None = None
    originator_account: str | None = None
    beneficiary_name: str | None = None
    beneficiary_account: str | None = None


@router.post("/check")
def check_transfer(to_address: str, amount: str):
    """Pre-check if a transfer would pass compliance."""
    amount_int = int(amount)
    ok, msg = run_compliance_checks(to_address, amount_int)
    s = get_settings()
    needs_travel_rule = amount_int >= s.travel_rule_threshold
    return {
        "allowed": ok,
        "reason": msg,
        "travel_rule_required": needs_travel_rule,
    }


@router.post("/execute")
def execute_transfer(req: TransferRequest, db: Session = Depends(get_db)):
    """Validate compliance and (when signer configured) execute. For MVP returns intent + travel rule payload."""
    amount_int = int(req.amount)
    ok, msg = run_compliance_checks(req.to_address, amount_int)
    if not ok:
        log(db, "transfer", req.from_address, amount=amount_int, counterparty=req.to_address, status="denied", reason=msg)
        raise HTTPException(403, msg)

    s = get_settings()
    travel_payload = None
    if amount_int >= s.travel_rule_threshold:
        travel_payload = create_payload(
            originator_name=req.originator_name or "Institution",
            originator_account=req.originator_account or req.from_address,
            beneficiary_name=req.beneficiary_name or "Beneficiary",
            beneficiary_account=req.beneficiary_account or req.to_address,
            amount=amount_int / 1e18,
        )
        store_for_tx(db, "pending_" + req.to_address[:10], travel_payload)

    log(db, "transfer", req.from_address, amount=amount_int, counterparty=req.to_address, status="success", metadata={"travel_rule": travel_payload is not None})
    return {
        "ok": True,
        "message": "Compliance passed. Configure backend signer to submit tx.",
        "travel_rule_payload": travel_payload,
    }
