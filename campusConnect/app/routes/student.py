"""
CampusConnect - Student Routes (Pure SQL)
==========================================
Student dashboard and event registration using raw PyMySQL queries.
No SQLAlchemy — all DB access via app.db.get_db().
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps

from ..db import get_db
from ..models import Event, Registration
from ..forms import StudentProfileForm
from ..utils.pagination import Pagination

student_bp = Blueprint("student", __name__, url_prefix="/student")


def student_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.__class__.__name__ != "Student":
            flash("You do not have permission to access this page.", "danger")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)
    return decorated_function


@student_bp.before_request
@student_required
def before_request():
    pass


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@student_bp.route("/dashboard")
def dashboard():
    conn = get_db()

    # Upcoming events the student is registered for
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT r.id, r.student_id, r.event_id, r.status, r.remarks,
                   r.registered_at, r.approved_at, r.cancelled_at, r.attendance_marked,
                   e.title AS event_title, e.event_date, e.venue AS event_venue
            FROM registrations r
            JOIN events e ON e.id = r.event_id
            WHERE r.student_id = %s AND e.event_date > NOW()
            ORDER BY e.event_date ASC
            LIMIT 3
            """,
            (current_user.id,)
        )
        upcoming_registrations = [Registration.from_row(r) for r in cur.fetchall()]

    # Recent published events
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, title, description, venue, event_date, total_seats, available_seats, status
            FROM events
            WHERE event_date > NOW() AND status = 'published'
            ORDER BY event_date ASC
            LIMIT 5
            """,
        )
        recent_events = [Event.from_row(r) for r in cur.fetchall()]

    return render_template(
        "student/dashboard.html",
        upcoming_registrations=upcoming_registrations,
        recent_events=recent_events,
    )


# ---------------------------------------------------------------------------
# Event catalog (with search + pagination)
# ---------------------------------------------------------------------------

@student_bp.route("/events")
def events():
    search   = request.args.get("search", "")
    page     = request.args.get("page", 1, type=int)
    per_page = 9
    offset   = (page - 1) * per_page
    conn     = get_db()

    base_where = "WHERE e.event_date > NOW() AND e.status = 'published'"
    params: list = []

    if search:
        base_where += " AND (e.title LIKE %s OR e.description LIKE %s)"
        like = f"%{search}%"
        params.extend([like, like])

    with conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) AS cnt FROM events e {base_where}", params)
        total = cur.fetchone()["cnt"]

        cur.execute(
            f"""
            SELECT e.id, e.title, e.description, e.venue, e.event_date,
                   e.total_seats, e.available_seats, e.status
            FROM events e
            {base_where}
            ORDER BY e.event_date ASC
            LIMIT %s OFFSET %s
            """,
            params + [per_page, offset]
        )
        items = [Event.from_row(r) for r in cur.fetchall()]

    # Collect all event IDs the student is already registered for
    with conn.cursor() as cur:
        cur.execute(
            "SELECT event_id FROM registrations WHERE student_id = %s",
            (current_user.id,)
        )
        registered_ids = {r["event_id"] for r in cur.fetchall()}

    pagination = Pagination(items, page, per_page, total)
    return render_template(
        "student/events.html",
        events_page=pagination,
        registered_ids=registered_ids,
        search=search,
    )


# ---------------------------------------------------------------------------
# Event detail
# ---------------------------------------------------------------------------

@student_bp.route("/events/<int:event_id>")
def event_detail(event_id):
    conn = get_db()

    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, title, description, venue, event_date, total_seats, available_seats, status "
            "FROM events WHERE id = %s",
            (event_id,)
        )
        row = cur.fetchone()

    if not row:
        flash("Event not found.", "warning")
        return redirect(url_for("student.events"))

    event = Event.from_row(row)

    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, student_id, event_id, status, remarks, registered_at, approved_at, "
            "cancelled_at, attendance_marked "
            "FROM registrations WHERE student_id = %s AND event_id = %s",
            (current_user.id, event_id)
        )
        reg_row = cur.fetchone()

    registration = Registration.from_row(reg_row) if reg_row else None

    return render_template(
        "student/event_detail.html",
        event=event,
        registration=registration,
    )


# ---------------------------------------------------------------------------
# Register for event (with row-level lock to prevent overbooking)
# ---------------------------------------------------------------------------

@student_bp.route("/events/<int:event_id>/register", methods=["POST"])
def register_event(event_id):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            # Lock the event row for update (prevents concurrent overbooking)
            cur.execute(
                "SELECT id, title, event_date, available_seats, status "
                "FROM events WHERE id = %s FOR UPDATE",
                (event_id,)
            )
            row = cur.fetchone()

        if not row:
            conn.rollback()
            flash("Event not found.", "danger")
            return redirect(url_for("student.events"))

        event = Event.from_row({
            "id": row["id"],
            "title": row["title"],
            "description": "",
            "venue": "",
            "event_date": row["event_date"],
            "total_seats": 0,
            "available_seats": row["available_seats"],
            "status": row["status"],
        })

        if not event.is_registration_open:
            conn.rollback()
            flash("Registration is closed or full.", "warning")
            return redirect(url_for("student.event_detail", event_id=event_id))

        # Check for duplicate registration
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM registrations WHERE student_id = %s AND event_id = %s",
                (current_user.id, event_id)
            )
            if cur.fetchone():
                conn.rollback()
                flash("You are already registered.", "info")
                return redirect(url_for("student.event_detail", event_id=event_id))

        # Decrement available seats and insert registration atomically
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE events SET available_seats = available_seats - 1 WHERE id = %s",
                (event_id,)
            )
            cur.execute(
                """
                INSERT INTO registrations (student_id, event_id, status, registered_at)
                VALUES (%s, %s, 'approved', NOW())
                """,
                (current_user.id, event_id)
            )
        conn.commit()
        flash(f"Successfully registered for {event.title}!", "success")

    except Exception:
        conn.rollback()
        flash("Registration failed. Please try again.", "danger")

    return redirect(url_for("student.event_detail", event_id=event_id))


# ---------------------------------------------------------------------------
# My registrations
# ---------------------------------------------------------------------------

@student_bp.route("/my-registrations")
def my_registrations():
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT r.id, r.student_id, r.event_id, r.status, r.remarks,
                   r.registered_at, r.approved_at, r.cancelled_at, r.attendance_marked,
                   e.title AS event_title, e.event_date, e.venue AS event_venue
            FROM registrations r
            JOIN events e ON e.id = r.event_id
            WHERE r.student_id = %s
            ORDER BY e.event_date DESC
            """,
            (current_user.id,)
        )
        registrations = [Registration.from_row(r) for r in cur.fetchall()]

    return render_template("student/my_registrations.html", registrations=registrations)


# ---------------------------------------------------------------------------
# Cancel registration
# ---------------------------------------------------------------------------

@student_bp.route("/registrations/<int:reg_id>/cancel", methods=["POST"])
def cancel_registration(reg_id):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, student_id, event_id FROM registrations WHERE id = %s",
            (reg_id,)
        )
        row = cur.fetchone()

    if not row or row["student_id"] != current_user.id:
        flash("Registration not found.", "danger")
        return redirect(url_for("student.my_registrations"))

    event_id = row["event_id"]

    # Check if the event is still upcoming (allow cancellation only for future events)
    with conn.cursor() as cur:
        cur.execute(
            "SELECT event_date FROM events WHERE id = %s FOR UPDATE",
            (event_id,)
        )
        event_row = cur.fetchone()

    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    if event_row and event_row["event_date"] > now:
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM registrations WHERE id = %s", (reg_id,))
                cur.execute(
                    "UPDATE events SET available_seats = available_seats + 1 WHERE id = %s",
                    (event_id,)
                )
            conn.commit()
            flash("Registration cancelled.", "success")
        except Exception:
            conn.rollback()
            flash("Failed to cancel registration.", "danger")
    else:
        conn.rollback()
        flash("Cannot cancel registration for past events.", "warning")

    return redirect(url_for("student.my_registrations"))


# ---------------------------------------------------------------------------
# Student profile update
# ---------------------------------------------------------------------------

@student_bp.route("/profile", methods=["GET", "POST"])
def profile():
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT id, name, code FROM departments ORDER BY name ASC")
        departments = cur.fetchall()

    form = StudentProfileForm(obj=current_user)
    form.department_id.choices = [(0, "Select Department")] + [
        (d["id"], f"{d['name']} ({d['code']})") for d in departments
    ]

    if request.method == "GET":
        form.department_id.data = current_user.department_id or 0

    if form.validate_on_submit():
        dept_id = form.department_id.data if form.department_id.data > 0 else None
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE students SET first_name = %s, last_name = %s, roll_number = %s, department_id = %s WHERE id = %s",
                    (
                        form.first_name.data,
                        form.last_name.data,
                        form.roll_number.data,
                        dept_id,
                        current_user.id,
                    ),
                )
            conn.commit()
            # Update the in-memory object so the page reflects changes immediately
            current_user.first_name    = form.first_name.data
            current_user.last_name     = form.last_name.data
            current_user.roll_number   = form.roll_number.data
            current_user.department_id = dept_id
            dept_dict = next((d for d in departments if d["id"] == dept_id), None)
            if dept_dict:
                current_user.department_name = dept_dict["name"]
                current_user.department_code = dept_dict["code"]
            flash("Profile updated successfully.", "success")
            return redirect(url_for("student.profile"))
        except Exception:
            conn.rollback()
            flash("Failed to update profile.", "danger")

    return render_template("student/profile.html", form=form)
