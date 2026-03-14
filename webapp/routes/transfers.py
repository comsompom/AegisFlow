from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from utils.api import get, post

transfers_bp = Blueprint("transfers", __name__)


@transfers_bp.route("/")
@login_required
def index():
    return render_template("transfer.html")


@transfers_bp.route("/check", methods=["POST"])
@login_required
def check():
    to_address = request.form.get("to_address", "").strip()
    amount = request.form.get("amount", "").strip()
    if not to_address or not amount:
        return {"allowed": False, "reason": "Address and amount required"}
    data = get(f"/api/transfers/check?to_address={to_address}&amount={amount}")
    return data if isinstance(data, dict) else {"allowed": False, "reason": "Check failed"}


@transfers_bp.route("/execute", methods=["POST"])
@login_required
def execute():
    from_address = request.form.get("from_address", "").strip()
    to_address = request.form.get("to_address", "").strip()
    amount = request.form.get("amount", "").strip()
    originator_name = request.form.get("originator_name", "").strip()
    beneficiary_name = request.form.get("beneficiary_name", "").strip()
    if not to_address or not amount:
        flash("Recipient and amount are required.", "danger")
        return redirect(url_for("transfers.index"))
    payload = {
        "from_address": from_address or "0x0000000000000000000000000000000000000000",
        "to_address": to_address,
        "amount": amount,
        "originator_name": originator_name or None,
        "originator_account": from_address or None,
        "beneficiary_name": beneficiary_name or None,
        "beneficiary_account": to_address,
    }
    data = post("/api/transfers/execute", json=payload)
    if data.get("error") or data.get("detail"):
        msg = data.get("detail")
        if isinstance(msg, dict) and "msg" in msg:
            msg = msg["msg"]
        elif isinstance(msg, list) and msg and "msg" in msg[0]:
            msg = msg[0]["msg"]
        flash(msg or data.get("error", "Transfer failed"), "danger")
    else:
        flash("Compliance passed. Configure backend signer to submit transaction.", "success")
        if data.get("travel_rule_payload"):
            flash("Travel Rule payload generated and stored.", "info")
    return redirect(url_for("transfers.index"))
