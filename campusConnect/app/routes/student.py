"""
CampusConnect - Student Routes
================================
Student dashboard and event registration.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from sqlalchemy import select

from ..extensions import db
from ..models import Event, Registration
from ..forms import StudentProfileForm

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

@student_bp.route("/dashboard")
def dashboard():
    upcoming_registrations = current_user.registrations.join(Event).filter(
        Event.event_date > db.func.now()
    ).order_by(Event.event_date.asc()).limit(3).all()
    
    recent_events = Event.query.filter(
        Event.event_date > db.func.now()
    ).order_by(Event.event_date.asc()).limit(5).all()
    
    return render_template(
        "student/dashboard.html",
        upcoming_registrations=upcoming_registrations,
        recent_events=recent_events
    )

@student_bp.route("/events")
def events():
    search = request.args.get("search", "")
    page = request.args.get("page", 1, type=int)

    query = Event.query.filter(Event.event_date > db.func.now())

    if search:
        query = query.filter(
            Event.title.ilike(f"%{search}%") |
            Event.description.ilike(f"%{search}%")
        )

    events_page = query.order_by(Event.event_date.asc()).paginate(
        page=page, per_page=9, error_out=False
    )

    registered_ids = {r.event_id for r in current_user.registrations.all()}

    return render_template(
        "student/events.html",
        events_page=events_page,
        registered_ids=registered_ids,
        search=search
    )

@student_bp.route("/events/<int:event_id>")
def event_detail(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        flash("Event not found.", "warning")
        return redirect(url_for("student.events"))

    registration = current_user.registrations.filter_by(event_id=event.id).first()

    return render_template(
        "student/event_detail.html",
        event=event,
        registration=registration
    )

@student_bp.route("/events/<int:event_id>/register", methods=["POST"])
def register_event(event_id):
    event = Event.query.with_for_update().get(event_id)
    if not event:
        flash("Event not found.", "danger")
        return redirect(url_for("student.events"))

    if not event.is_registration_open:
        flash("Registration is closed or full.", "warning")
        db.session.rollback()
        return redirect(url_for("student.event_detail", event_id=event.id))

    existing = current_user.registrations.filter_by(event_id=event.id).first()
    if existing:
        flash("You are already registered.", "info")
        db.session.rollback()
        return redirect(url_for("student.event_detail", event_id=event.id))

    event.available_seats -= 1
    
    reg = Registration(
        student_id=current_user.id,
        event_id=event.id,
        status="approved"
    )
    db.session.add(reg)
    db.session.commit()
    
    flash(f"Successfully registered for {event.title}!", "success")
    return redirect(url_for("student.event_detail", event_id=event.id))

@student_bp.route("/my-registrations")
def my_registrations():
    registrations = current_user.registrations.join(Event).order_by(
        Event.event_date.desc()
    ).all()
    
    return render_template("student/my_registrations.html", registrations=registrations)

@student_bp.route("/registrations/<int:reg_id>/cancel", methods=["POST"])
def cancel_registration(reg_id):
    reg = db.session.get(Registration, reg_id)
    if not reg or reg.student_id != current_user.id:
        flash("Registration not found.", "danger")
        return redirect(url_for("student.my_registrations"))

    if reg.event.is_registration_open:
        event = Event.query.with_for_update().get(reg.event_id)
        event.available_seats += 1
        db.session.delete(reg)
        db.session.commit()
        flash("Registration cancelled.", "success")
    else:
        flash("Cannot cancel registration for past events.", "warning")
        
    return redirect(url_for("student.my_registrations"))

@student_bp.route("/profile", methods=["GET", "POST"])
def profile():
    form = StudentProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.roll_number = form.roll_number.data
        
        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("student.profile"))
        
    return render_template("student/profile.html", form=form)
