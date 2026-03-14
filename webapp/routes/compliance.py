from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from utils.api import get, post, delete

compliance_bp = Blueprint("compliance", __name__)


@compliance_bp.route("/")
@login_required
def whitelist():
    # Backend doesn't expose full list; we show form and check endpoint
    return render_template("whitelist.html")


@compliance_bp.route("/check/<address>")
@login_required
def check(address):
    data = get(f"/api/compliance/whitelist/{address}")
    return data if isinstance(data, dict) else {"whitelisted": False}


@compliance_bp.route("/add", methods=["POST"])
@login_required
def add():
    address = request.form.get("address", "").strip()
    if not address:
        flash("Address is required.", "danger")
        return redirect(url_for("compliance.whitelist"))
    data = post("/api/compliance/whitelist", json={"address": address})
    if data.get("error") or data.get("detail"):
        flash(data.get("detail") or data.get("error", "Failed to add"), "danger")
    else:
        flash("Whitelist request submitted (configure backend signer to execute).", "success")
    return redirect(url_for("compliance.whitelist"))


@compliance_bp.route("/remove", methods=["POST"])
@login_required
def remove():
    address = request.form.get("address", "").strip()
    if not address:
        flash("Address is required.", "danger")
        return redirect(url_for("compliance.whitelist"))
    data = delete("/api/compliance/whitelist", json={"address": address})
    if data.get("error"):
        flash(data.get("error", "Failed to remove"), "danger")
    else:
        flash("Remove request submitted.", "success")
    return redirect(url_for("compliance.whitelist"))


@compliance_bp.route("/blacklist", methods=["POST"])
@login_required
def blacklist():
    address = request.form.get("address", "").strip()
    if not address:
        flash("Address is required.", "danger")
        return redirect(url_for("compliance.whitelist"))
    data = post("/api/compliance/blacklist", json={"address": address})
    if data.get("error") or data.get("detail"):
        flash(data.get("detail") or data.get("error", "Failed to blacklist"), "danger")
    else:
        flash("Blacklist request submitted.", "success")
    return redirect(url_for("compliance.whitelist"))
