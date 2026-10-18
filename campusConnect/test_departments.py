"""
Test Suite for Department Feature & CampusConnect APIs
======================================================
Tests:
- Database schema and department seeder
- Student registration with department selection
- Student profile viewing and updating department
- Student browsing and registering for events
- Admin login and dashboard
- Admin student listing (verifying Department column & value)
- Admin event registration listing (verifying Department column & value)
"""

from run import app


def run_tests():
    print("Testing application startup and client...")
    client = app.test_client()

    # 1. Test GET /
    res = client.get("/")
    assert res.status_code == 200, f"GET / failed with {res.status_code}"
    print("[PASS] GET / -> 200 OK")

    # 2. Test GET /auth/register and check departments are present
    res = client.get("/auth/register")
    assert res.status_code == 200, f"GET /auth/register failed with {res.status_code}"
    assert (
        b"Computer Science &amp; Engineering" in res.data
        or b"Computer Science & Engineering" in res.data
        or b"CSE" in res.data
    ), "Departments not rendered in register page"
    print("[PASS] GET /auth/register -> 200 OK (Contains seeded departments)")

    # 3. Test Student Registration with Department
    test_email = "dept.test@student.campusconnect.com"
    test_roll = "DEP999"

    with app.app_context():
        from app.db import get_db

        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM students WHERE email = %s OR roll_number = %s",
                (test_email, test_roll),
            )
            cur.execute("SELECT id FROM departments WHERE code = %s", ("CSE",))
            cse_id = cur.fetchone()["id"]
        conn.commit()

    # POST registration
    app.config["WTF_CSRF_ENABLED"] = False
    res = client.post(
        "/auth/register",
        data={
            "first_name": "TestDept",
            "last_name": "Student",
            "email": test_email,
            "roll_number": test_roll,
            "department_id": cse_id,
            "password": "Password@123",
            "confirm_password": "Password@123",
        },
        follow_redirects=True,
    )

    assert (
        res.status_code == 200
    ), f"POST /auth/register failed with {res.status_code}"
    assert (
        b"Account created successfully!" in res.data or b"Dashboard" in res.data
    ), "Registration redirect failed"
    print(
        "[PASS] POST /auth/register with department -> 200 OK (Account created & logged in)"
    )

    # 4. Verify in DB
    with app.app_context():
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT s.id, s.first_name, s.department_id, d.name AS dept_name 
                FROM students s 
                JOIN departments d ON d.id = s.department_id 
                WHERE s.email = %s
            """,
                (test_email,),
            )
            row = cur.fetchone()
            assert row is not None, "Student record not found in DB"
            assert (
                row["dept_name"] == "Computer Science & Engineering"
            ), f"Incorrect dept: {row}"
            student_id = row["id"]
    print(
        f"[PASS] Database Verification -> Student {test_email} linked to {row['dept_name']}"
    )

    # 5. Test Student Profile GET & POST (change department to IT)
    with app.app_context():
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM departments WHERE code = %s", ("IT",))
            it_id = cur.fetchone()["id"]

    res = client.get("/student/profile")
    assert (
        res.status_code == 200
    ), f"GET /student/profile failed with {res.status_code}"

    res = client.post(
        "/student/profile",
        data={
            "first_name": "TestDeptUpdated",
            "last_name": "Student",
            "roll_number": test_roll,
            "department_id": it_id,
        },
        follow_redirects=True,
    )
    assert (
        res.status_code == 200
    ), f"POST /student/profile failed with {res.status_code}"
    assert (
        b"Profile updated successfully." in res.data
    ), "Profile update flash message not found"
    print(
        "[PASS] POST /student/profile (Updated department to IT) -> 200 OK"
    )

    # 6. Test Event Registration as Student
    res = client.get("/student/events")
    assert (
        res.status_code == 200
    ), f"GET /student/events failed with {res.status_code}"

    with app.app_context():
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute('SELECT id FROM events WHERE status = "published" LIMIT 1')
            event_id = cur.fetchone()["id"]

    res = client.post(
        f"/student/events/{event_id}/register", follow_redirects=True
    )
    assert (
        res.status_code == 200
    ), f"POST register for event failed: {res.status_code}"
    print(f"[PASS] POST /student/events/{event_id}/register -> 200 OK")

    # 7. Logout Student
    res = client.get("/auth/logout", follow_redirects=True)
    assert res.status_code == 200
    print("[PASS] Student logged out")

    # 8. Admin Login
    res = client.post(
        "/auth/admin/login",
        data={
            "email": "admin@campusconnect.com",
            "password": "Admin@123",
        },
        follow_redirects=True,
    )
    assert res.status_code == 200, f"Admin login failed: {res.status_code}"
    assert b"Admin Dashboard" in res.data, "Admin dashboard not reached"
    print("[PASS] POST /auth/admin-login -> 200 OK (Logged in as Admin)")

    # 9. Test Admin Students list (/admin/students) and verify Department column & name
    res = client.get("/admin/students")
    assert (
        res.status_code == 200
    ), f"GET /admin/students failed: {res.status_code}"
    assert (
        b"Department" in res.data
    ), "Department column header missing from /admin/students"
    assert (
        b"Information Technology" in res.data
    ), "Student department name missing from /admin/students table"
    print(
        "[PASS] GET /admin/students -> 200 OK (Department column & Information Technology displayed)"
    )

    # 10. Test Admin Event Registrations (/admin/events/<id>/registrations) and verify Department
    res = client.get(f"/admin/events/{event_id}/registrations")
    assert (
        res.status_code == 200
    ), f"GET /admin/events/{event_id}/registrations failed: {res.status_code}"
    assert (
        b"Department" in res.data
    ), "Department column header missing from /admin/events/<id>/registrations"
    assert (
        b"Information Technology" in res.data
    ), "Registered student department missing from registrations table"
    print(
        f"[PASS] GET /admin/events/{event_id}/registrations -> 200 OK (Department displayed in registrations table)"
    )

    # 11. Test Admin Approve Registration
    with app.app_context():
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM registrations WHERE student_id = %s AND event_id = %s",
                (student_id, event_id),
            )
            reg_id = cur.fetchone()["id"]

    res = client.post(
        f"/admin/registrations/{reg_id}/status",
        data={"status": "approved"},
        follow_redirects=True,
    )
    assert res.status_code == 200
    assert b"Registration status updated." in res.data
    print(
        "[PASS] POST /admin/registrations/<id>/status -> 200 OK (Registration approved)"
    )

    # Cleanup test student
    with app.app_context():
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM students WHERE id = %s", (student_id,))
        conn.commit()
    print("[PASS] Cleanup test data complete")
    print("\n==========================================")
    print("  ALL API & WORKFLOW TESTS PASSED (100%)  ")
    print("==========================================")


if __name__ == "__main__":
    run_tests()
