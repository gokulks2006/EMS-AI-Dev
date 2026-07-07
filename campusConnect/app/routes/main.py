"""
CampusConnect - Main/Landing Page Routes
==========================================
Handles the public-facing home page and general redirects.
"""

from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from ..models import Event, Student, Admin
from ..extensions import db

# Create main blueprint - no URL prefix (root routes)
main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """
    Landing page / home page.
    Shows upcoming events and platform statistics.
    Redirects authenticated users to their respective dashboards.
    """
    # Redirect authenticated users to their dashboards
    if current_user.is_authenticated:
        if isinstance(current_user, Admin):
            return redirect(url_for("admin.dashboard"))
        elif isinstance(current_user, Student):
            return redirect(url_for("student.dashboard"))

    # Fetch featured/upcoming published events for the landing page
    upcoming_events = (
        Event.query
        .filter_by(status="published")
        .order_by(Event.event_date.asc())
        .limit(6)
        .all()
    )

    # Platform-wide statistics for the hero section
    stats = {
        "total_events": Event.query.filter_by(status="published").count(),
        "total_students": Student.query.filter_by(is_active=True).count(),
        "total_registrations": db.session.execute(
            db.text("SELECT COUNT(*) FROM registrations")
        ).scalar() or 0,
    }

    return render_template("main/index.html",
                           upcoming_events=upcoming_events,
                           stats=stats)


@main_bp.route("/about")
def about():
    """About page with project/college information."""
    return render_template("main/about.html")
