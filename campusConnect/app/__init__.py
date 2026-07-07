"""
CampusConnect - Application Factory
=====================================
Uses the Application Factory Pattern to create a Flask app instance.
This allows creating multiple app instances (e.g., for testing) with
different configurations without modifying global state.

Why factory pattern?
- Avoids circular imports
- Allows multiple app instances (testing, production)
- Centralizes extension initialization
- Enables blueprint registration in one place
"""

import os
from flask import Flask, render_template
from .config import config_map
from .extensions import db, login_manager, bcrypt, migrate, csrf


def create_app(config_name: str = "default") -> Flask:
    """
    Application factory function.

    Args:
        config_name: One of 'development', 'testing', 'production', 'default'

    Returns:
        Configured Flask application instance
    """

    # ------------------------------------------------------------------
    # Create Flask app with explicit template and static paths
    # ------------------------------------------------------------------
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )

    # ------------------------------------------------------------------
    # Load configuration from config_map
    # ------------------------------------------------------------------
    config_class = config_map.get(config_name, config_map["default"])
    app.config.from_object(config_class)

    # ------------------------------------------------------------------
    # Ensure upload directory exists
    # ------------------------------------------------------------------
    upload_dir = app.config.get("UPLOAD_FOLDER", "app/static/uploads")
    os.makedirs(upload_dir, exist_ok=True)

    # ------------------------------------------------------------------
    # Initialize extensions with the app instance
    # ------------------------------------------------------------------
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # ------------------------------------------------------------------
    # Register Flask Blueprints (route modules)
    # Each blueprint handles a section of the application
    # ------------------------------------------------------------------
    _register_blueprints(app)

    # ------------------------------------------------------------------
    # Register custom error handlers
    # ------------------------------------------------------------------
    _register_error_handlers(app)

    # ------------------------------------------------------------------
    # Register CLI commands (manage.py equivalents)
    # ------------------------------------------------------------------
    _register_commands(app)

    # ------------------------------------------------------------------
    # Context processors - inject variables into all templates
    # ------------------------------------------------------------------
    _register_context_processors(app)

    return app


def _register_blueprints(app: Flask) -> None:
    """Register all route blueprints with the application."""

    from .routes.auth import auth_bp
    from .routes.admin import admin_bp
    from .routes.student import student_bp
    from .routes.main import main_bp

    app.register_blueprint(main_bp)               # / (home, landing page)
    app.register_blueprint(auth_bp, url_prefix="/auth")     # /auth/login, /auth/register
    app.register_blueprint(admin_bp, url_prefix="/admin")   # /admin/dashboard
    app.register_blueprint(student_bp, url_prefix="/student")  # /student/dashboard


def _register_error_handlers(app: Flask) -> None:
    """Register HTTP error page handlers."""

    @app.errorhandler(403)
    def forbidden(e):
        """403 Forbidden - User lacks permission."""
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        """404 Not Found - Page does not exist."""
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        """500 Internal Server Error - Unexpected application error."""
        return render_template("errors/500.html"), 500


def _register_commands(app: Flask) -> None:
    """Register custom Flask CLI commands."""

    @app.cli.command("seed-db")
    def seed_db():
        """Seed the database with initial admin and sample data."""
        from .utils.seed import seed_database
        seed_database()
        print("✓ Database seeded successfully.")

    @app.cli.command("create-admin")
    def create_admin():
        """Create default admin user."""
        from .utils.seed import create_default_admin
        create_default_admin()
        print("✓ Default admin created.")

    @app.cli.command("reset-db")
    def reset_db():
        """Drop all tables and recreate (dev only)."""
        db.drop_all()
        db.create_all()
        print("✓ Database reset complete.")


def _register_context_processors(app: Flask) -> None:
    """
    Context processors inject variables into ALL Jinja2 templates automatically.
    Avoids passing the same variables in every route's render_template() call.
    """

    @app.context_processor
    def inject_globals():
        """Inject app name and current year into every template."""
        from datetime import datetime
        return {
            "app_name": "CampusConnect",
            "current_year": datetime.now().year,
        }
