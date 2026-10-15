"""
CampusConnect - Main/Landing Page Routes (Pure SQL)
=====================================================
Handles the public-facing home page and general redirects.
No SQLAlchemy — all DB access via app.db.get_db().
"""

from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

from ..db import get_db
from ..models import Event, Student, Admin

# Create main blueprint - no URL prefix (root routes)
main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """
    Landing page / home page.
    Shows upcoming published events and platform statistics.
    Redirects authenticated users to their respective dashboards.
    """
    # Redirect authenticated users to their dashboards
    if current_user.is_authenticated:
        if isinstance(current_user, Admin):
            return redirect(url_for("admin.dashboard"))
        elif isinstance(current_user, Student):
            return redirect(url_for("student.dashboard"))

    conn = get_db()

    # Fetch featured/upcoming published events for the landing page
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, title, description, venue, event_date,
                   total_seats, available_seats, status
            FROM events
            WHERE status = 'published' AND event_date > NOW()
            ORDER BY event_date ASC
            LIMIT 6
            """
        )
        upcoming_events = [Event.from_row(r) for r in cur.fetchall()]

    # Platform-wide statistics for the hero section
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS cnt FROM events WHERE status = 'published'")
        total_events = cur.fetchone()["cnt"]

        cur.execute("SELECT COUNT(*) AS cnt FROM students")
        total_students = cur.fetchone()["cnt"]

        cur.execute("SELECT COUNT(*) AS cnt FROM registrations")
        total_registrations = cur.fetchone()["cnt"]

    stats = {
        "total_events":        total_events,
        "total_students":      total_students,
        "total_registrations": total_registrations,
    }

    return render_template(
        "main/index.html",
        upcoming_events=upcoming_events,
        stats=stats,
    )


@main_bp.route("/about")
def about():
    """About page with project/college information."""
    return render_template("main/about.html")
