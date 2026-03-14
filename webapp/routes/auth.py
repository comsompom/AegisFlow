from flask import Blueprint, redirect, url_for, request, render_template, flash
from flask_login import login_user, logout_user, login_required, current_user
from config import Config

from models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if username == Config.DEMO_USER and password == Config.DEMO_PASSWORD:
            user = User(username, "compliance")
            login_user(user)
            flash("Logged in successfully.", "success")
            next_url = request.args.get("next") or url_for("dashboard.index")
            return redirect(next_url)
        flash("Invalid username or password.", "danger")
    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
