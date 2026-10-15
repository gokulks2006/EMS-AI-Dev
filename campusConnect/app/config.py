"""
CampusConnect - Application Configuration (Pure SQL edition)
=============================================================
Defines configuration classes for different environments.
SQLAlchemy-specific keys (SQLALCHEMY_*) have been removed.
Database connection is done via PyMySQL using individual DB_* keys.

Environments:
  - DevConfig   : Development (MySQL via .env, debug mode on)
  - ProdConfig  : Production  (MySQL via env vars, secure cookies)
  - default     : DevConfig
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Base configuration class.
    All environment-specific configs inherit from this.
    """

    # ------------------------------------------------------------------
    # Flask Core
    # ------------------------------------------------------------------
    SECRET_KEY = os.environ.get("SECRET_KEY", "fallback-secret-key-change-me")
    WTF_CSRF_ENABLED = True      # Enable CSRF protection on all forms
    WTF_CSRF_TIME_LIMIT = 3600   # CSRF token valid for 1 hour

    # ------------------------------------------------------------------
    # Database — PyMySQL connection parameters
    # (No SQLALCHEMY_DATABASE_URI — we use raw SQL via PyMySQL)
    # ------------------------------------------------------------------
    DB_HOST     = os.environ.get("DB_HOST", "localhost")
    DB_PORT     = os.environ.get("DB_PORT", "3306")
    DB_NAME     = os.environ.get("DB_NAME", "campusconnect")
    DB_USER     = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "root")

    # ------------------------------------------------------------------
    # Session
    # ------------------------------------------------------------------
    PERMANENT_SESSION_LIFETIME = timedelta(
        seconds=int(os.environ.get("SESSION_TIMEOUT", 3600))
    )
    SESSION_COOKIE_HTTPONLY = True   # JS cannot access session cookie
    SESSION_COOKIE_SAMESITE = "Lax"  # CSRF protection

    # ------------------------------------------------------------------
    # File Uploads
    # ------------------------------------------------------------------
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))
    UPLOAD_FOLDER      = os.environ.get("UPLOAD_FOLDER", "app/static/uploads")
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

    # ------------------------------------------------------------------
    # Pagination
    # ------------------------------------------------------------------
    EVENTS_PER_PAGE   = 9    # Cards per page on event listing
    STUDENTS_PER_PAGE = 20   # Rows per page in admin student table
    LOGS_PER_PAGE     = 50   # Audit log rows per page

    # ------------------------------------------------------------------
    # Mail (optional - graceful degradation if not configured)
    # ------------------------------------------------------------------
    MAIL_SERVER   = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT     = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS  = os.environ.get("MAIL_USE_TLS", "True") == "True"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")


class DevConfig(Config):
    """
    Development configuration.
    Enables debug mode. Uses MySQL from .env by default.
    """
    DEBUG = True
    SESSION_COOKIE_SECURE = False   # Allow HTTP in dev


class ProdConfig(Config):
    """
    Production configuration.
    Enforces HTTPS cookies and disables debug output.
    """
    DEBUG = False
    SESSION_COOKIE_SECURE = True    # Only send cookie over HTTPS


# Mapping string names to config classes (used in app factory)
config_map = {
    "development": DevConfig,
    "production":  ProdConfig,
    "default":     DevConfig,
}
