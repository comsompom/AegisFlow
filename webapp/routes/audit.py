from flask import Blueprint, render_template, request
from flask_login import login_required
from utils.api import get

audit_bp = Blueprint("audit", __name__)


@audit_bp.route("/")
@login_required
def index():
    action = request.args.get("action")
    data = get(f"/api/audit/log?limit=100" + (f"&action={action}" if action else ""))
    entries = data.get("entries", []) if isinstance(data, dict) else []
    return render_template("audit.html", entries=entries)


@audit_bp.route("/travel-rule")
@login_required
def travel_rule_list():
    data = get("/api/audit/travel-rule")
    payloads = data.get("payloads", []) if isinstance(data, dict) else []
    return render_template("travel_rule.html", payloads=payloads)


@audit_bp.route("/travel-rule/<tx_hash>")
@login_required
def travel_rule_by_tx(tx_hash):
    data = get(f"/api/audit/travel-rule/{tx_hash}")
    return render_template("travel_rule_detail.html", tx_hash=tx_hash, data=data)
