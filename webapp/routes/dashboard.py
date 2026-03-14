from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

from utils.api import get

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))
    return render_template("index.html")


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    limits = get("/api/compliance/limits") or {}
    health = get("/health") or {}
    return render_template("dashboard.html", limits=limits, health=health)
