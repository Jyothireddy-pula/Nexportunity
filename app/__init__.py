from flask import Flask

from app.extensions import register_extensions
from app.logging_config import configure_logging
from config.settings import get_config
from routes.dashboard import dashboard_bp
from routes.export import export_bp
from routes.health import health_bp
from routes.api import api_bp
from routes.analytics import analytics_bp
from scheduler.jobs import start_scheduler
from services.email_service import EmailService, EmailConfig


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object(get_config(config_name))

    configure_logging(app)
    register_extensions(app)

    with app.app_context():
        from models.opportunity import Opportunity  # noqa: F401
        from app.extensions import db

        db.create_all()

    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(export_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(analytics_bp)

    # Configure email service
    email_config = EmailConfig(
        enabled=app.config.get("EMAIL_ENABLED", False),
        smtp_server=app.config.get("SMTP_SERVER", ""),
        smtp_port=app.config.get("SMTP_PORT", 587),
        smtp_username=app.config.get("SMTP_USERNAME", ""),
        smtp_password=app.config.get("SMTP_PASSWORD", ""),
        from_email=app.config.get("FROM_EMAIL", ""),
        to_emails=app.config.get("TO_EMAILS", [])
    )
    EmailService.configure(email_config)

    @app.get("/api/stats")
    def stats():
        from models.opportunity import Opportunity

        total = Opportunity.query.count()
        grants = Opportunity.query.filter_by(opportunity_type="grant").count()
        accelerators = Opportunity.query.filter_by(opportunity_type="accelerator").count()
        return {
            "total": total,
            "grants": grants,
            "accelerators": accelerators,
        }

    if app.config.get("ENABLE_SCHEDULER", True) and not app.config.get("TESTING", False):
        start_scheduler()

    return app
