"""
CampusConnect - Database Seed Utility
========================================
Seeds the database with initial data for development and demo.

Creates:
  - Default super admin account
  - Sample events
  - Sample students
"""

from datetime import datetime, timedelta
from ..extensions import db, bcrypt


def create_default_admin():
    """
    Create the default super admin account.
    Credentials are read from environment variables.
    Only creates if no admin exists yet.
    """
    import os
    from ..models.admin import Admin

    existing = Admin.query.first()
    if existing:
        print("Admin already exists, skipping.")
        return

    admin = Admin(
        name="System Administrator",
        email=os.environ.get("ADMIN_EMAIL", "admin@campusconnect.com"),
    )
    admin.set_password(os.environ.get("ADMIN_PASSWORD", "Admin@123"))
    db.session.add(admin)
    db.session.commit()
    print(f"[SUCCESS] Admin created: {admin.email}")


def seed_departments():
    """Seed standard college departments (No-op as the table is not in the schema)."""
    print("Skipping department seeding (not in database schema).")


def seed_sample_students():
    """Seed sample student accounts for testing."""
    from ..models.student import Student

    students_data = [
        {
            "first_name": "Arjun",
            "last_name": "Mehta",
            "email": "arjun.mehta@student.campusconnect.com",
            "roll_number": "CSE2024001",
        },
        {
            "first_name": "Priya",
            "last_name": "Singh",
            "email": "priya.singh@student.campusconnect.com",
            "roll_number": "CSE2024002",
        },
        {
            "first_name": "Rahul",
            "last_name": "Gupta",
            "email": "rahul.gupta@student.campusconnect.com",
            "roll_number": "CSE2024003",
        },
    ]

    for student_data in students_data:
        existing = Student.query.filter_by(email=student_data["email"]).first()
        if not existing:
            student = Student(**student_data)
            student.set_password("Student@123")
            db.session.add(student)

    db.session.commit()
    print(f"[SUCCESS] {len(students_data)} students seeded.")


def seed_sample_events():
    """Seed sample events for testing."""
    from ..models.event import Event

    now = datetime.utcnow()

    events_data = [
        {
            "title": "National Tech Fest 2024",
            "description": "Annual technical festival featuring hackathons, coding contests, robotics, and paper presentations. Open to all engineering students.",
            "venue": "Main Auditorium, Block A",
            "event_date": now + timedelta(days=15),
            "total_seats": 200,
            "available_seats": 200,
            "status": "published",
        },
        {
            "title": "AI & Machine Learning Workshop",
            "description": "Hands-on workshop on deep learning fundamentals using PyTorch. Covers neural networks, CNNs, and real-world projects.",
            "venue": "CS Lab 301",
            "event_date": now + timedelta(days=7),
            "total_seats": 50,
            "available_seats": 50,
            "status": "published",
        },
        {
            "title": "Cultural Night 2024",
            "description": "Annual cultural celebration with music, dance, drama, and stand-up comedy. A night to remember!",
            "venue": "Open Air Theatre",
            "event_date": now + timedelta(days=30),
            "total_seats": 500,
            "available_seats": 500,
            "status": "published",
        },
        {
            "title": "Electronics Design Challenge",
            "description": "Design and build embedded systems projects. Best projects win cash prizes and internship opportunities.",
            "venue": "ECE Lab 205",
            "event_date": now + timedelta(days=20),
            "total_seats": 80,
            "available_seats": 80,
            "status": "published",
        },
        {
            "title": "Sports Day 2024",
            "description": "Inter-department sports competition including cricket, football, badminton, and athletics.",
            "venue": "College Sports Complex",
            "event_date": now + timedelta(days=45),
            "total_seats": 300,
            "available_seats": 300,
            "status": "published",
        },
    ]

    for event_data in events_data:
        existing = Event.query.filter_by(title=event_data["title"]).first()
        if not existing:
            event = Event(**event_data)
            db.session.add(event)

    db.session.commit()
    print(f"[SUCCESS] {len(events_data)} sample events seeded.")


def seed_database():
    """Run all seed functions in dependency order."""
    print("Seeding database...")
    create_default_admin()
    seed_departments()
    seed_sample_students()
    seed_sample_events()
    print("[SUCCESS] Database seeding complete!")
