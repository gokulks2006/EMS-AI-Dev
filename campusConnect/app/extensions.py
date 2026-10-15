"""
CampusConnect - Flask Extensions (Pure SQL edition)
=====================================================
Centralizes Flask extension instances to avoid circular imports.

Removed:
  - flask_sqlalchemy (SQLAlchemy) — replaced by app/db.py (PyMySQL)
  - flask_migrate    (Alembic)   — replaced by flask init-db

Kept:
  - Flask-Login  : Session management & current_user
  - Flask-Bcrypt : Password hashing
  - Flask-WTF    : CSRF protection
"""

from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect

# ------------------------------------------------------------------
# Flask-Login - Session management for authentication
# Handles user session, login_required decorator, current_user
# ------------------------------------------------------------------
login_manager = LoginManager()
login_manager.login_view = "auth.login"          # Redirect if not authenticated
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "warning"

# ------------------------------------------------------------------
# Flask-Bcrypt - Password hashing using bcrypt algorithm
# bcrypt is intentionally slow to prevent brute-force attacks
# ------------------------------------------------------------------
bcrypt = Bcrypt()

# ------------------------------------------------------------------
# Flask-WTF CSRFProtect - Global CSRF token validation
# Protects all POST/PUT/DELETE forms from CSRF attacks
# ------------------------------------------------------------------
csrf = CSRFProtect()
