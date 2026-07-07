"""
CampusConnect - Database Seed Utility
========================================
Seeds the database with initial data for development and demo.

Creates:
  - Default departments
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
        is_super_admin=True,
        is_active=True,
    )
    admin.set_password(os.environ.get("ADMIN_PASSWORD", "Admin@123"))
    db.session.add(admin)
    db.session.commit()
    print(f"✓ Admin created: {admin.email}")


def seed_departments():
    """Seed standard college departments."""
    from ..models.department import Department

    departments_data = [
        {"name": "Computer Science & Engineering", "code": "CSE",
         "description": "Computing, algorithms, and software engineering.",
         "head_of_dept": "Dr. Rajesh Kumar"},
        {"name": "Electronics & Communication", "code": "ECE",
         "description": "Electronics, signals, and communications.",
         "head_of_dept": "Dr. Priya Sharma"},
        {"name": "Mechanical Engineering", "code": "ME",
         "description": "Design, manufacturing, and thermal systems.",
         "head_of_dept": "Dr. Anil Verma"},
        {"name": "Civil Engineering", "code": "CE",
         "description": "Structural, environmental, and geotechnical engineering.",
         "head_of_dept": "Dr. Sunita Patel"},
        {"name": "Electrical Engineering", "code": "EE",
         "description": "Power systems and electrical machines.",
         "head_of_dept": "Dr. Mohan Das"},
        {"name": "Information Technology", "code": "IT",
         "description": "IT systems, networking, and data management.",
         "head_of_dept": "Dr. Kavitha Nair"},
    ]

    for dept_data in departments_data:
        existing = Department.query.filter_by(code=dept_data["code"]).first()
        if not existing:
            dept = Department(**dept_data)
            db.session.add(dept)

    db.session.commit()
    print(f"✓ {len(departments_data)} departments seeded.")


def seed_sample_students():
    """Seed sample student accounts for testing."""
    from ..models.student import Student
    from ..models.department import Department

    cse_dept = Department.query.filter_by(code="CSE").first()

    students_data = [
        {
            "first_name": "Arjun", "last_name": "Mehta",
            "email": "arjun.mehta@student.campusconnect.com",
            "roll_number": "CSE2024001", "year_of_study": 3,
            "phone": "9876543210",
        },
        {
            "first_name": "Priya", "last_name": "Singh",
            "email": "priya.singh@student.campusconnect.com",
            "roll_number": "CSE2024002", "year_of_study": 2,
            "phone": "9876543211",
        },
        {
            "first_name": "Rahul", "last_name": "Gupta",
            "email": "rahul.gupta@student.campusconnect.com",
            "roll_number": "CSE2024003", "year_of_study": 4,
            "phone": "9876543212",
        },
    ]

    for student_data in students_data:
        existing = Student.query.filter_by(email=student_data["email"]).first()
        if not existing:
            student = Student(**student_data, department_id=cse_dept.id if cse_dept else None)
            student.set_password("Student@123")
            db.session.add(student)

    db.session.commit()
    print(f"✓ {len(students_data)} students seeded.")


def seed_sample_events():
    """Seed sample events for all departments."""
    from ..models.event import Event
    from ..models.admin import Admin
    from ..models.department import Department

    admin = Admin.query.first()
    cse_dept = Department.query.filter_by(code="CSE").first()
    ece_dept = Department.query.filter_by(code="ECE").first()

    now = datetime.utcnow()

    events_data = [
        {
            "title": "National Tech Fest 2024",
            "description": "Annual technical festival featuring hackathons, coding contests, robotics, and paper presentations. Open to all engineering students.",
            "short_description": "Annual tech fest with hackathons, coding contests & robotics!",
            "venue": "Main Auditorium, Block A",
            "event_date": now + timedelta(days=15),
            "registration_deadline": now + timedelta(days=10),
            "total_seats": 200, "available_seats": 200,
            "category": "Technical", "status": "published",
            "is_free": True, "banner_color": "#6366f1",
            "department_id": cse_dept.id if cse_dept else None,
        },
        {
            "title": "AI & Machine Learning Workshop",
            "description": "Hands-on workshop on deep learning fundamentals using PyTorch. Covers neural networks, CNNs, and real-world projects.",
            "short_description": "Deep learning hands-on workshop with PyTorch.",
            "venue": "CS Lab 301",
            "event_date": now + timedelta(days=7),
            "registration_deadline": now + timedelta(days=5),
            "total_seats": 50, "available_seats": 50,
            "category": "Workshop", "status": "published",
            "is_free": False, "fee_amount": 299.00,
            "banner_color": "#10b981",
            "department_id": cse_dept.id if cse_dept else None,
        },
        {
            "title": "Cultural Night 2024",
            "description": "Annual cultural celebration with music, dance, drama, and stand-up comedy. A night to remember!",
            "short_description": "Music, dance, drama and stand-up comedy night!",
            "venue": "Open Air Theatre",
            "event_date": now + timedelta(days=30),
            "registration_deadline": now + timedelta(days=25),
            "total_seats": 500, "available_seats": 500,
            "category": "Cultural", "status": "published",
            "is_free": True, "banner_color": "#f59e0b",
            "department_id": None,
        },
        {
            "title": "Electronics Design Challenge",
            "description": "Design and build embedded systems projects. Best projects win cash prizes and internship opportunities.",
            "short_description": "Design embedded systems and win prizes!",
            "venue": "ECE Lab 205",
            "event_date": now + timedelta(days=20),
            "registration_deadline": now + timedelta(days=15),
            "total_seats": 80, "available_seats": 80,
            "category": "Technical", "status": "published",
            "is_free": True, "banner_color": "#3b82f6",
            "department_id": ece_dept.id if ece_dept else None,
        },
        {
            "title": "Sports Day 2024",
            "description": "Inter-department sports competition including cricket, football, badminton, and athletics.",
            "short_description": "Inter-department sports: cricket, football, badminton!",
            "venue": "College Sports Complex",
            "event_date": now + timedelta(days=45),
            "registration_deadline": now + timedelta(days=40),
            "total_seats": 300, "available_seats": 300,
            "category": "Sports", "status": "published",
            "is_free": True, "banner_color": "#ef4444",
            "department_id": None,
        },
    ]

    for event_data in events_data:
        existing = Event.query.filter_by(title=event_data["title"]).first()
        if not existing:
            event = Event(**event_data, created_by=admin.id if admin else None)
            db.session.add(event)

    db.session.commit()
    print(f"✓ {len(events_data)} sample events seeded.")


def seed_database():
    """Run all seed functions in dependency order."""
    print("Seeding database...")
    create_default_admin()
    seed_departments()
    seed_sample_students()
    seed_sample_events()
    print("✓ Database seeding complete!")
