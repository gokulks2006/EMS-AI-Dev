"""
CampusConnect - Application Factory (Pure SQL edition)
=======================================================
Uses the Application Factory Pattern to create a Flask app instance.
Database layer: PyMySQL via app/db.py (no SQLAlchemy ORM).

Why factory pattern?
- Avoids circular imports
- Allows multiple app instances (testing, production)
- Centralizes extension initialization
- Enables blueprint registration in one place
"""

import os
from flask import Flask, render_template
from .config import config_map
from .extensions import login_manager, bcrypt, csrf
from .db import init_db_teardown


def create_app(config_name: str = "default") -> Flask:
    """
    Application factory function.

    Args:
        config_name: One of 'development', 'production', 'default'

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
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)

    # ------------------------------------------------------------------
    # Register DB teardown (close PyMySQL connection per-request)
    # ------------------------------------------------------------------
    init_db_teardown(app)

    # ------------------------------------------------------------------
    # Register the Flask-Login user_loader using raw SQL
    # ------------------------------------------------------------------
    _register_user_loader()

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
    # Register context processors - inject variables into all templates
    # ------------------------------------------------------------------
    _register_context_processors(app)

    # ------------------------------------------------------------------
    # Prevent browser caching of protected pages (back-button security)
    # ------------------------------------------------------------------
    _register_no_cache_headers(app)

    return app


def _register_user_loader() -> None:
    """
    Register Flask-Login's user_loader using raw SQL.
    Loads Admin or Student from the database by session token.
    Token format:  'a_<id>'  → Admin
                   's_<id>'  → Student
    """
    from .extensions import login_manager
    from .models import Admin, Student

    @login_manager.user_loader
    def load_user(user_id: str):
        from .db import get_db
        conn = get_db()
        try:
            if user_id.startswith("a_"):
                admin_id = int(user_id[2:])
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT id, name, email, password_hash FROM admins WHERE id = %s",
                        (admin_id,)
                    )
                    row = cur.fetchone()
                return Admin.from_row(row) if row else None

            elif user_id.startswith("s_"):
                student_id = int(user_id[2:])
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT s.id, s.first_name, s.last_name, s.email, s.password_hash,
                               s.roll_number, s.is_active, s.department_id,
                               d.name AS department_name, d.code AS department_code
                        FROM students s
                        LEFT JOIN departments d ON d.id = s.department_id
                        WHERE s.id = %s
                        """,
                        (student_id,)
                    )
                    row = cur.fetchone()
                return Student.from_row(row) if row else None
        except Exception:
            return None
        return None


def _register_blueprints(app: Flask) -> None:
    """Register all route blueprints with the application."""

    from .routes.auth import auth_bp
    from .routes.admin import admin_bp
    from .routes.student import student_bp
    from .routes.main import main_bp

    app.register_blueprint(main_bp)                         # /
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

    @app.cli.command("init-db")
    def init_db():
        """Create all tables (run once on fresh setup)."""
        from .db import get_db, create_tables
        with app.app_context():
            conn = get_db()
            create_tables(conn)

    @app.cli.command("reset-db")
    def reset_db():
        """Drop all tables and recreate (dev only)."""
        from .db import get_db, drop_tables, create_tables
        with app.app_context():
            conn = get_db()
            drop_tables(conn)
            create_tables(conn)
            print("[SUCCESS] Database reset complete.")

    @app.cli.command("seed-db")
    def seed_db():
        """Seed the database with initial admin and sample data."""
        from .utils.seed import seed_database
        seed_database()
        print("[SUCCESS] Database seeded successfully.")

    @app.cli.command("create-admin")
    def create_admin():
        """Create default admin user."""
        from .utils.seed import create_default_admin
        create_default_admin()
        print("[SUCCESS] Default admin created.")


def _register_context_processors(app: Flask) -> None:
    """
    Context processors inject variables into ALL Jinja2 templates automatically.
    Avoids passing the same variables in every route's render_template() call.
    """

    @app.context_processor
    def inject_globals():
        """Inject app name, current year, and current datetime into every template."""
        from datetime import datetime
        return {
            "app_name": "CampusConnect",
            "current_year": datetime.now().year,
            "now": datetime.utcnow(),
        }


def _register_no_cache_headers(app: Flask) -> None:
    """
    Prevent browser from caching protected pages.
    After logout, pressing back should NOT show protected content.
    """

    @app.after_request
    def set_no_cache(response):
        """Set no-cache headers on all responses to prevent back-button visual bugs."""
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
