"""AegisFlow Flask Web Application — Institutional Control Room."""
from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from config import Config
from routes.auth import auth_bp
from routes.compliance import compliance_bp
from routes.limits import limits_bp
from routes.transfers import transfers_bp
from routes.ai_agent import ai_agent_bp
from routes.audit import audit_bp
from routes.dashboard import dashboard_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    CSRFProtect(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."

    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        if user_id == config_class.DEMO_USER:
            return User(user_id, "compliance")
        return None

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(dashboard_bp, url_prefix="/")
    app.register_blueprint(compliance_bp, url_prefix="/compliance")
    app.register_blueprint(limits_bp, url_prefix="/limits")
    app.register_blueprint(transfers_bp, url_prefix="/transfers")
    app.register_blueprint(ai_agent_bp, url_prefix="/ai")
    app.register_blueprint(audit_bp, url_prefix="/audit")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
