"""
CampusConnect - Flask Extensions
=================================
Centralizes all Flask extension instances so they can be imported
anywhere without creating circular imports.

Pattern: Initialize here without app, then call init_app() in the
         application factory (app/__init__.py).
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

# ------------------------------------------------------------------
# SQLAlchemy - ORM for MySQL
# Provides database models, sessions, and query interface
# ------------------------------------------------------------------
db = SQLAlchemy()

# ------------------------------------------------------------------
# Flask-Login - Session management for authentication
# Handles user session, login_required decorator, current_user
# ------------------------------------------------------------------
login_manager = LoginManager()
login_manager.login_view = "auth.login"          # Redirect to login if not authenticated
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "warning"

# ------------------------------------------------------------------
# Flask-Bcrypt - Password hashing using bcrypt algorithm
# bcrypt is intentionally slow to prevent brute-force attacks
# ------------------------------------------------------------------
bcrypt = Bcrypt()

# ------------------------------------------------------------------
# Flask-Migrate - Database migration management via Alembic
# Allows schema changes without dropping/recreating tables
# ------------------------------------------------------------------
migrate = Migrate()

# ------------------------------------------------------------------
# Flask-WTF CSRFProtect - Global CSRF token validation
# Protects all POST/PUT/DELETE forms from CSRF attacks
# ------------------------------------------------------------------
csrf = CSRFProtect()
