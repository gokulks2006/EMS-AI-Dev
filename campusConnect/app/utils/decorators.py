"""
CampusConnect - Custom Decorators
====================================
Provides route protection decorators beyond Flask-Login's @login_required.

Why custom decorators?
  - Flask-Login's @login_required only checks authentication
  - We need role-based access control (admin vs student)
  - We need to prevent students from accessing admin routes
  - Composable with @login_required for layered security
"""

from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user


def admin_required(f):
    """
    Decorator that restricts a route to authenticated admin users only.

    Usage:
        @admin_bp.route('/dashboard')
        @login_required
        @admin_required
        def dashboard():
            ...

    Why: Students should never access admin routes even if somehow authenticated.
    How: Checks current_user is an Admin instance (not Student).
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from app.models import Admin
        if not current_user.is_authenticated:
            flash("Please log in as admin to access this page.", "warning")
            return redirect(url_for("auth.admin_login"))
        if not isinstance(current_user, Admin):
            flash("Access denied. Administrator privileges required.", "danger")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)
    return decorated_function


def student_required(f):
    """
    Decorator that restricts a route to authenticated student users only.

    Why: Admins should not access student-facing routes (separate UX).
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from app.models import Student
        if not current_user.is_authenticated:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth.login"))
        if not isinstance(current_user, Student):
            flash("Access denied. This page is for students only.", "danger")
            return redirect(url_for("main.index"))
        if not current_user.is_active:
            flash("Your account has been deactivated. Contact admin.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


def super_admin_required(f):
    """
    Decorator that restricts access to super admins only.
    Used for creating new admins and system-level operations.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from app.models import Admin
        if not isinstance(current_user, Admin) or not current_user.is_super_admin:
            flash("Super Administrator privileges required.", "danger")
            return redirect(url_for("admin.dashboard"))
        return f(*args, **kwargs)
    return decorated_function
