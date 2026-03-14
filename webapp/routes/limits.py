from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from utils.api import get, post

limits_bp = Blueprint("limits", __name__)


@limits_bp.route("/")
@login_required
def index():
    data = get("/api/compliance/limits")
    if not data or "error" in data:
        data = {"maxPerTx": 0, "maxDailyVolume": 0, "dailyVolumeUsed": 0}
    return render_template("limits.html", limits=data)


@limits_bp.route("/update", methods=["POST"])
@login_required
def update():
    max_per_tx = request.form.get("max_per_tx", "").strip()
    max_daily = request.form.get("max_daily_volume", "").strip()
    if not max_per_tx or not max_daily:
        flash("Both fields are required.", "danger")
        return redirect(url_for("limits.index"))
    data = post("/api/compliance/limits", json={
        "max_per_tx": max_per_tx,
        "max_daily_volume": max_daily,
    })
    if data.get("error") or data.get("detail"):
        flash(data.get("detail") or data.get("error", "Failed to update limits"), "danger")
    else:
        flash("Limits update submitted (configure backend signer to execute).", "success")
    return redirect(url_for("limits.index"))
