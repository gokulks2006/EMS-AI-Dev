"""
CampusConnect - Registration Model (Pure SQL)
================================================
Plain Python class that mirrors the `registrations` table.
No ORM — all database interaction happens through raw SQL.

Transaction Flow (enforced in routes with raw SQL):
  BEGIN TRANSACTION
    → SELECT available_seats ... FOR UPDATE   (lock the event row)
    → Check available_seats > 0
    → INSERT INTO registrations
    → UPDATE events SET available_seats = available_seats - 1
  COMMIT  (or ROLLBACK on any failure)
"""

from datetime import datetime


class Registration:
    """
    Represents a row from the `registrations` table.
    Junction between students and events.

    Status workflow: pending → approved → attended
                  or pending → rejected
                  or approved → cancelled
    """

    def __init__(
        self,
        id: int,
        student_id: int,
        event_id: int,
        status: str = "pending",
        remarks: str = None,
        registered_at: datetime = None,
        approved_at: datetime = None,
        cancelled_at: datetime = None,
        attendance_marked: bool = False,
        # Optional joined columns (populated when joining with other tables)
        event_title: str = None,
        event_date: datetime = None,
        event_venue: str = None,
        student_name: str = None,
        student_roll_number: str = None,
        student_email: str = None,
    ):
        self.id                  = id
        self.student_id          = student_id
        self.event_id            = event_id
        self.status              = status
        self.remarks             = remarks
        self.registered_at       = registered_at or datetime.utcnow()
        self.approved_at         = approved_at
        self.cancelled_at        = cancelled_at
        self.attendance_marked   = bool(attendance_marked)
        # Denormalized / joined fields for display convenience
        self.event_title         = event_title
        self.event_date          = event_date
        self.event_venue         = event_venue
        self.student_name        = student_name
        self.student_roll_number = student_roll_number
        self.student_email       = student_email

    @property
    def event(self):
        """Return an Event object or proxy for template compatibility (e.g. reg.event.title)."""
        from .event import Event
        return Event(
            id=self.event_id,
            title=self.event_title or "",
            description="",
            venue=self.event_venue or "",
            event_date=self.event_date or datetime.utcnow(),
            total_seats=0,
            available_seats=0,
            status="",
        )

    @property
    def student(self):
        """Return a Student-like proxy for template compatibility (e.g. reg.student.full_name)."""
        class _StudentProxy:
            def __init__(self, full_name, roll_number, email):
                self.full_name = full_name or ""
                self.roll_number = roll_number or ""
                self.email = email or ""

        return _StudentProxy(
            full_name=self.student_name,
            roll_number=self.student_roll_number,
            email=self.student_email,
        )

    # ------------------------------------------------------------------
    # SQL helpers — build Registration from a DB row dict
    # ------------------------------------------------------------------

    @classmethod
    def from_row(cls, row: dict) -> "Registration":
        """
        Construct a Registration instance from a pymysql DictCursor row.
        Handles both plain rows and rows enriched by JOINs.
        """
        return cls(
            id=row["id"],
            student_id=row["student_id"],
            event_id=row["event_id"],
            status=row.get("status", "pending"),
            remarks=row.get("remarks"),
            registered_at=row.get("registered_at"),
            approved_at=row.get("approved_at"),
            cancelled_at=row.get("cancelled_at"),
            attendance_marked=row.get("attendance_marked", False),
            # Joined columns (present only in JOINed queries)
            event_title=row.get("event_title") or row.get("title"),
            event_date=row.get("event_date"),
            event_venue=row.get("event_venue") or row.get("venue"),
            student_name=row.get("student_name"),
            student_roll_number=row.get("roll_number") or row.get("student_roll_number"),
            student_email=row.get("student_email") or row.get("email"),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "student_id": self.student_id,
            "event_id": self.event_id,
            "status": self.status,
            "registered_at": self.registered_at.isoformat() if self.registered_at else None,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
        }

    def __repr__(self):
        return f"<Registration Student:{self.student_id} Event:{self.event_id} [{self.status}]>"
