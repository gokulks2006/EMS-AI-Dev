"""
CampusConnect - Authentication Routes
======================================
Handles login, registration, and logout.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from ..extensions import db
from ..models import Student, Admin
from ..forms import StudentLoginForm, AdminLoginForm, StudentRegistrationForm

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        if isinstance(current_user, Admin):
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("student.dashboard"))

    form = StudentRegistrationForm()

    if form.validate_on_submit():
        existing = Student.query.filter_by(email=form.email.data.lower().strip()).first()
        if existing:
            flash("An account with this email already exists.", "warning")
            return render_template("auth/register.html", form=form)

        try:
            student = Student(
                first_name=form.first_name.data.strip(),
                last_name=form.last_name.data.strip(),
                email=form.email.data.lower().strip(),
                roll_number=form.roll_number.data.strip().upper(),
                password=form.password.data
            )
            db.session.add(student)
            db.session.commit()

            login_user(student)
            flash("Account created successfully!", "success")
            return redirect(url_for("student.dashboard"))

        except Exception as e:
            db.session.rollback()
            flash("Registration failed due to a system error. Please try again.", "danger")

    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if isinstance(current_user, Admin):
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("student.dashboard"))

    form = StudentLoginForm()

    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        student = Student.query.filter_by(email=email).first()

        if not student or not student.check_password(form.password.data):
            flash("Invalid email or password. Please try again.", "danger")
            return render_template("auth/login.html", form=form)

        login_user(student, remember=form.remember_me.data)
        
        next_page = request.args.get("next")
        if next_page and next_page.startswith("/"):
            return redirect(next_page)
        return redirect(url_for("student.dashboard"))

    return render_template("auth/login.html", form=form)


@auth_bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if current_user.is_authenticated:
        if isinstance(current_user, Admin):
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("student.dashboard"))

    form = AdminLoginForm()

    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        admin = Admin.query.filter_by(email=email).first()

        if not admin or not admin.check_password(form.password.data):
            flash("Invalid admin credentials.", "danger")
            return render_template("auth/admin_login.html", form=form)

        login_user(admin, remember=False)
        flash(f"Welcome back, {admin.name}!", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("auth/admin_login.html", form=form)


@auth_bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    from flask import make_response
    resp = make_response(redirect(url_for("main.index")))
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    return resp
