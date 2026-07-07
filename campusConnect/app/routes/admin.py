"""
CampusConnect - Admin Routes
==============================
CRUD operations for Events and Registrations.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps

from ..extensions import db
from ..models import Event, Registration, Student
from ..forms import EventForm

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

@admin_bp.route("/dashboard")
def dashboard():
    total_events = Event.query.count()
    total_students = Student.query.count()
    total_registrations = Registration.query.count()
    
    recent_events = Event.query.order_by(Event.event_date.desc()).limit(5).all()
    
    return render_template(
        "admin/dashboard.html",
        total_events=total_events,
        total_students=total_students,
        total_registrations=total_registrations,
        recent_events=recent_events
    )

@admin_bp.route("/events")
def events():
    page = request.args.get("page", 1, type=int)
    events_page = Event.query.order_by(Event.event_date.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template("admin/events.html", events_page=events_page)

@admin_bp.route("/events/new", methods=["GET", "POST"])
def event_new():
    form = EventForm()
    
    if form.validate_on_submit():
        event = Event(
            title=form.title.data,
            description=form.description.data,
            venue=form.venue.data,
            event_date=form.event_date.data,
            total_seats=form.total_seats.data,
            available_seats=form.total_seats.data
        )
        db.session.add(event)
        db.session.commit()
        flash("Event created successfully.", "success")
        return redirect(url_for("admin.events"))
        
    return render_template("admin/event_form.html", form=form, edit_mode=False)

@admin_bp.route("/events/<int:event_id>/edit", methods=["GET", "POST"])
def event_edit(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        flash("Event not found.", "danger")
        return redirect(url_for("admin.events"))
        
    form = EventForm(obj=event)
    
    if form.validate_on_submit():
        event.title = form.title.data
        event.description = form.description.data
        event.venue = form.venue.data
        event.event_date = form.event_date.data
        
        # Calculate new available seats if total_seats changes
        diff = form.total_seats.data - event.total_seats
        event.total_seats = form.total_seats.data
        event.available_seats += diff
        
        db.session.commit()
        flash("Event updated successfully.", "success")
        return redirect(url_for("admin.events"))
        
    return render_template("admin/event_form.html", form=form, event=event, edit_mode=True)

@admin_bp.route("/events/<int:event_id>/delete", methods=["POST"])
def event_delete(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        flash("Event not found.", "danger")
        return redirect(url_for("admin.events"))
        
    db.session.delete(event)
    db.session.commit()
    flash("Event deleted.", "success")
    return redirect(url_for("admin.events"))

@admin_bp.route("/events/<int:event_id>/registrations")
def registrations(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        flash("Event not found.", "danger")
        return redirect(url_for("admin.events"))
        
    regs = event.registrations.order_by(Registration.id.desc()).all()
    return render_template("admin/registrations.html", event=event, registrations=regs)

@admin_bp.route("/registrations/<int:reg_id>/status", methods=["POST"])
def update_registration_status(reg_id):
    reg = db.session.get(Registration, reg_id)
    if not reg:
        flash("Registration not found.", "danger")
        return redirect(url_for("admin.events"))
        
    status = request.form.get("status")
    if status in ["approved", "rejected"]:
        reg.status = status
        db.session.commit()
        flash("Registration status updated.", "success")
        
    return redirect(url_for("admin.registrations", event_id=reg.event_id))

@admin_bp.route("/students")
def students():
    page = request.args.get("page", 1, type=int)
    students_page = Student.query.order_by(Student.last_name).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template("admin/students.html", students_page=students_page)
