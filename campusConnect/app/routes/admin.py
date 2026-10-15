"""
CampusConnect - Admin Routes (Pure SQL)
=========================================
CRUD operations for Events and Registrations using raw PyMySQL queries.
No SQLAlchemy — all DB access via app.db.get_db().
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps

from ..db import get_db
from ..models import Event, Registration, Student
from ..forms import EventForm
from ..utils.pagination import Pagination

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.__class__.__name__ != "Admin":
            flash("You do not have permission to access this page.", "danger")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.before_request
@admin_required
def before_request():
    pass


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@admin_bp.route("/dashboard")
def dashboard():
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS cnt FROM events")
        total_events = cur.fetchone()["cnt"]

        cur.execute("SELECT COUNT(*) AS cnt FROM students")
        total_students = cur.fetchone()["cnt"]

        cur.execute("SELECT COUNT(*) AS cnt FROM registrations")
        total_registrations = cur.fetchone()["cnt"]

        cur.execute(
            "SELECT id, title, description, venue, event_date, total_seats, available_seats, status "
            "FROM events ORDER BY event_date DESC LIMIT 5"
        )
        recent_events = [Event.from_row(r) for r in cur.fetchall()]

    return render_template(
        "admin/dashboard.html",
        total_events=total_events,
        total_students=total_students,
        total_registrations=total_registrations,
        recent_events=recent_events,
    )


# ---------------------------------------------------------------------------
# Event listing with manual pagination
# ---------------------------------------------------------------------------

@admin_bp.route("/events")
def events():
    page     = request.args.get("page", 1, type=int)
    per_page = 10
    offset   = (page - 1) * per_page
    conn     = get_db()

    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS cnt FROM events")
        total = cur.fetchone()["cnt"]

        cur.execute(
            "SELECT id, title, description, venue, event_date, total_seats, available_seats, status "
            "FROM events ORDER BY event_date DESC LIMIT %s OFFSET %s",
            (per_page, offset)
        )
        items = [Event.from_row(r) for r in cur.fetchall()]

    # Build a simple pagination object for the template
    total_pages = (total + per_page - 1) // per_page
    pagination = {
        "items": items,
        "page": page,
        "pages": total_pages,
        "total": total,
        "has_prev": page > 1,
        "has_next": page < total_pages,
        "prev_num": page - 1,
        "next_num": page + 1,
    }
    return render_template("admin/events.html", events_page=pagination)


# ---------------------------------------------------------------------------
# Create event
# ---------------------------------------------------------------------------

@admin_bp.route("/events/new", methods=["GET", "POST"])
def event_new():
    form = EventForm()

    if form.validate_on_submit():
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO events (title, description, venue, event_date,
                                        total_seats, available_seats, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        form.title.data,
                        form.description.data,
                        form.venue.data,
                        form.event_date.data,
                        form.total_seats.data,
                        form.total_seats.data,   # available = total at creation
                        "published",
                    ),
                )
            conn.commit()
            flash("Event created successfully.", "success")
            return redirect(url_for("admin.events"))
        except Exception:
            conn.rollback()
            flash("Failed to create event. Please try again.", "danger")

    return render_template("admin/event_form.html", form=form, edit_mode=False)


# ---------------------------------------------------------------------------
# Edit event
# ---------------------------------------------------------------------------

@admin_bp.route("/events/<int:event_id>/edit", methods=["GET", "POST"])
def event_edit(event_id):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, title, description, venue, event_date, total_seats, available_seats, status "
            "FROM events WHERE id = %s",
            (event_id,)
        )
        row = cur.fetchone()

    if not row:
        flash("Event not found.", "danger")
        return redirect(url_for("admin.events"))

    event = Event.from_row(row)
    form  = EventForm(obj=event)

    if form.validate_on_submit():
        # Recalculate available seats when total changes
        diff = form.total_seats.data - event.total_seats
        new_available = event.available_seats + diff

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE events
                    SET title = %s, description = %s, venue = %s, event_date = %s,
                        total_seats = %s, available_seats = %s
                    WHERE id = %s
                    """,
                    (
                        form.title.data,
                        form.description.data,
                        form.venue.data,
                        form.event_date.data,
                        form.total_seats.data,
                        new_available,
                        event_id,
                    ),
                )
            conn.commit()
            flash("Event updated successfully.", "success")
            return redirect(url_for("admin.events"))
        except Exception:
            conn.rollback()
            flash("Failed to update event.", "danger")

    return render_template("admin/event_form.html", form=form, event=event, edit_mode=True)


# ---------------------------------------------------------------------------
# Delete event
# ---------------------------------------------------------------------------

@admin_bp.route("/events/<int:event_id>/delete", methods=["POST"])
def event_delete(event_id):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM events WHERE id = %s", (event_id,))
        if not cur.fetchone():
            flash("Event not found.", "danger")
            return redirect(url_for("admin.events"))

    try:
        with conn.cursor() as cur:
            # ON DELETE CASCADE handles registrations automatically
            cur.execute("DELETE FROM events WHERE id = %s", (event_id,))
        conn.commit()
        flash("Event deleted.", "success")
    except Exception:
        conn.rollback()
        flash("Failed to delete event.", "danger")

    return redirect(url_for("admin.events"))


# ---------------------------------------------------------------------------
# Registrations for an event
# ---------------------------------------------------------------------------

@admin_bp.route("/events/<int:event_id>/registrations")
def registrations(event_id):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, title, description, venue, event_date, total_seats, available_seats, status "
            "FROM events WHERE id = %s",
            (event_id,)
        )
        event_row = cur.fetchone()

    if not event_row:
        flash("Event not found.", "danger")
        return redirect(url_for("admin.events"))

    event = Event.from_row(event_row)

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT r.id, r.student_id, r.event_id, r.status, r.remarks,
                   r.registered_at, r.approved_at, r.cancelled_at, r.attendance_marked,
                   CONCAT(s.first_name, ' ', s.last_name) AS student_name,
                   s.roll_number, s.email AS student_email
            FROM registrations r
            JOIN students s ON s.id = r.student_id
            WHERE r.event_id = %s
            ORDER BY r.id DESC
            """,
            (event_id,)
        )
        regs = [Registration.from_row(r) for r in cur.fetchall()]

    return render_template("admin/registrations.html", event=event, registrations=regs)


# ---------------------------------------------------------------------------
# Update registration status
# ---------------------------------------------------------------------------

@admin_bp.route("/registrations/<int:reg_id>/status", methods=["POST"])
def update_registration_status(reg_id):
    conn   = get_db()
    status = request.form.get("status")

    with conn.cursor() as cur:
        cur.execute("SELECT id, event_id, status FROM registrations WHERE id = %s", (reg_id,))
        row = cur.fetchone()

    if not row:
        flash("Registration not found.", "danger")
        return redirect(url_for("admin.events"))

    if status in ("approved", "rejected"):
        try:
            with conn.cursor() as cur:
                if status == "approved":
                    cur.execute(
                        "UPDATE registrations SET status = %s, approved_at = NOW() WHERE id = %s",
                        (status, reg_id)
                    )
                else:
                    cur.execute(
                        "UPDATE registrations SET status = %s WHERE id = %s",
                        (status, reg_id)
                    )
            conn.commit()
            flash("Registration status updated.", "success")
        except Exception:
            conn.rollback()
            flash("Failed to update status.", "danger")

    return redirect(url_for("admin.registrations", event_id=row["event_id"]))


# ---------------------------------------------------------------------------
# Students listing
# ---------------------------------------------------------------------------

@admin_bp.route("/students")
def students():
    page     = request.args.get("page", 1, type=int)
    per_page = 20
    offset   = (page - 1) * per_page
    conn     = get_db()

    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS cnt FROM students")
        total = cur.fetchone()["cnt"]

        cur.execute(
            "SELECT id, first_name, last_name, email, roll_number, is_active "
            "FROM students ORDER BY last_name ASC LIMIT %s OFFSET %s",
            (per_page, offset)
        )
        items = [Student.from_row(r) for r in cur.fetchall()]

    total_pages = (total + per_page - 1) // per_page
    pagination = {
        "items": items,
        "page": page,
        "pages": total_pages,
        "total": total,
        "has_prev": page > 1,
        "has_next": page < total_pages,
        "prev_num": page - 1,
        "next_num": page + 1,
    }
    return render_template("admin/students.html", students_page=pagination)
