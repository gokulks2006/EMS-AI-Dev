"""
CampusConnect - Authentication Routes (Pure SQL)
=================================================
Handles login, registration, and logout using raw PyMySQL queries.
No SQLAlchemy — all DB access via app.db.get_db().
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user

from ..db import get_db
from ..models import Student, Admin
from ..models.student import Student as StudentModel
from ..forms import StudentLoginForm, AdminLoginForm, StudentRegistrationForm

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        if isinstance(current_user, Admin):
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("student.dashboard"))

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT id, name, code FROM departments ORDER BY name ASC")
        departments = cur.fetchall()

    form = StudentRegistrationForm()
    form.department_id.choices = [(0, "Select Department")] + [
        (d["id"], f"{d['name']} ({d['code']})") for d in departments
    ]

    if form.validate_on_submit():
        email       = form.email.data.lower().strip()
        roll_number = form.roll_number.data.strip().upper()

        # Check for duplicate email
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM students WHERE email = %s", (email,))
            if cur.fetchone():
                flash("An account with this email already exists.", "warning")
                return render_template("auth/register.html", form=form)

        # Check for duplicate roll number
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM students WHERE roll_number = %s", (roll_number,))
            if cur.fetchone():
                flash("An account with this roll number already exists.", "warning")
                return render_template("auth/register.html", form=form)

        password_hash = StudentModel.hash_password(form.password.data)

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO students (first_name, last_name, email, password_hash, roll_number, department_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        form.first_name.data.strip(),
                        form.last_name.data.strip(),
                        email,
                        password_hash,
                        roll_number,
                        form.department_id.data,
                    ),
                )
                new_id = cur.lastrowid
            conn.commit()

            # Load the new student and log them in
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT s.id, s.first_name, s.last_name, s.email, s.password_hash, s.roll_number, s.is_active,
                           s.department_id, d.name AS department_name, d.code AS department_code
                    FROM students s
                    LEFT JOIN departments d ON d.id = s.department_id
                    WHERE s.id = %s
                    """,
                    (new_id,)
                )
                row = cur.fetchone()
            student = Student.from_row(row)
            login_user(student)
            flash("Account created successfully!", "success")
            return redirect(url_for("student.dashboard"))

        except Exception as e:
            conn.rollback()
            current_app.logger.error(f"Registration error: {e}", exc_info=True)
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
        conn  = get_db()

        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT s.id, s.first_name, s.last_name, s.email, s.password_hash, s.roll_number, s.is_active,
                       s.department_id, d.name AS department_name, d.code AS department_code
                FROM students s
                LEFT JOIN departments d ON d.id = s.department_id
                WHERE s.email = %s
                """,
                (email,)
            )
            row = cur.fetchone()

        if not row:
            flash("Invalid email or password. Please try again.", "danger")
            return render_template("auth/login.html", form=form)

        student = Student.from_row(row)

        if not student.check_password(form.password.data):
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
        conn  = get_db()

        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, email, password_hash FROM admins WHERE email = %s",
                (email,)
            )
            row = cur.fetchone()

        if not row:
            flash("Invalid admin credentials.", "danger")
            return render_template("auth/admin_login.html", form=form)

        admin = Admin.from_row(row)

        if not admin.check_password(form.password.data):
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
