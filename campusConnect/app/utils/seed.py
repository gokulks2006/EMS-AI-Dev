"""
CampusConnect - Database Seed Utility (Pure SQL)
==================================================
Seeds the database with initial data for development and demo.
No SQLAlchemy — all DB access via app.db.get_db().

Creates:
  - Default super admin account
  - Sample events
  - Sample students
"""

import os
from datetime import datetime, timedelta
from ..db import get_db
from ..models.admin import Admin
from ..models.student import Student


def create_default_admin():
    """
    Create the default super admin account.
    Credentials are read from environment variables.
    Only creates if no admin exists yet.
    """
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM admins LIMIT 1")
        if cur.fetchone():
            print("Admin already exists, skipping.")
            return

    admin_email = os.environ.get("ADMIN_EMAIL", "admin@campusconnect.com")
    admin_name  = "System Administrator"
    password    = os.environ.get("ADMIN_PASSWORD", "Admin@123")
    pw_hash     = Admin.hash_password(password)

    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO admins (name, email, password_hash) VALUES (%s, %s, %s)",
            (admin_name, admin_email, pw_hash)
        )
    conn.commit()
    print(f"[SUCCESS] Admin created: {admin_email}")


def seed_sample_students():
    """Seed sample student accounts for testing."""
    conn = get_db()

    students_data = [
        {
            "first_name": "Arjun",
            "last_name":  "Mehta",
            "email":       "arjun.mehta@student.campusconnect.com",
            "roll_number": "CSE2024001",
        },
        {
            "first_name": "Priya",
            "last_name":  "Singh",
            "email":       "priya.singh@student.campusconnect.com",
            "roll_number": "CSE2024002",
        },
        {
            "first_name": "Rahul",
            "last_name":  "Gupta",
            "email":       "rahul.gupta@student.campusconnect.com",
            "roll_number": "CSE2024003",
        },
    ]

    inserted = 0
    for s in students_data:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM students WHERE email = %s", (s["email"],))
            if cur.fetchone():
                continue

        pw_hash = Student.hash_password("Student@123")
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO students (first_name, last_name, email, password_hash, roll_number) "
                "VALUES (%s, %s, %s, %s, %s)",
                (s["first_name"], s["last_name"], s["email"], pw_hash, s["roll_number"])
            )
        inserted += 1

    conn.commit()
    print(f"[SUCCESS] {inserted} student(s) seeded.")


def seed_sample_events():
    """Seed sample events for testing."""
    conn = get_db()
    now  = datetime.utcnow()

    events_data = [
        {
            "title":           "National Tech Fest 2024",
            "description":     "Annual technical festival featuring hackathons, coding contests, robotics, and paper presentations. Open to all engineering students.",
            "venue":           "Main Auditorium, Block A",
            "event_date":      now + timedelta(days=15),
            "total_seats":     200,
            "available_seats": 200,
            "status":          "published",
        },
        {
            "title":           "AI & Machine Learning Workshop",
            "description":     "Hands-on workshop on deep learning fundamentals using PyTorch. Covers neural networks, CNNs, and real-world projects.",
            "venue":           "CS Lab 301",
            "event_date":      now + timedelta(days=7),
            "total_seats":     50,
            "available_seats": 50,
            "status":          "published",
        },
        {
            "title":           "Cultural Night 2024",
            "description":     "Annual cultural celebration with music, dance, drama, and stand-up comedy. A night to remember!",
            "venue":           "Open Air Theatre",
            "event_date":      now + timedelta(days=30),
            "total_seats":     500,
            "available_seats": 500,
            "status":          "published",
        },
        {
            "title":           "Electronics Design Challenge",
            "description":     "Design and build embedded systems projects. Best projects win cash prizes and internship opportunities.",
            "venue":           "ECE Lab 205",
            "event_date":      now + timedelta(days=20),
            "total_seats":     80,
            "available_seats": 80,
            "status":          "published",
        },
        {
            "title":           "Sports Day 2024",
            "description":     "Inter-department sports competition including cricket, football, badminton, and athletics.",
            "venue":           "College Sports Complex",
            "event_date":      now + timedelta(days=45),
            "total_seats":     300,
            "available_seats": 300,
            "status":          "published",
        },
    ]

    inserted = 0
    for e in events_data:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM events WHERE title = %s", (e["title"],))
            if cur.fetchone():
                continue

        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO events (title, description, venue, event_date,
                                    total_seats, available_seats, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    e["title"], e["description"], e["venue"], e["event_date"],
                    e["total_seats"], e["available_seats"], e["status"]
                )
            )
        inserted += 1

    conn.commit()
    print(f"[SUCCESS] {inserted} event(s) seeded.")


def seed_database():
    """Run all seed functions in dependency order."""
    print("Seeding database...")
    create_default_admin()
    seed_sample_students()
    seed_sample_events()
    print("[SUCCESS] Database seeding complete!")
