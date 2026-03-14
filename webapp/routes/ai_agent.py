from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required
from utils.api import get, post

ai_agent_bp = Blueprint("ai_agent", __name__)


@ai_agent_bp.route("/")
@login_required
def index():
    status = get("/api/ai/status") or {}
    proposals = get("/api/ai/proposals") or {}
    return render_template("ai_agent.html", status=status, proposals=proposals.get("proposals", []))


@ai_agent_bp.route("/run-once", methods=["POST"])
@login_required
def run_once():
    data = post("/api/ai/run-once")
    if data.get("error") or data.get("detail"):
        flash(data.get("detail") or data.get("error", "Run failed"), "danger")
    else:
        flash("AI agent run completed. Check proposals.", "success")
    return redirect(url_for("ai_agent.index"))


@ai_agent_bp.route("/proposals")
@login_required
def proposals():
    data = get("/api/ai/proposals")
    return jsonify(data or {"proposals": []})
