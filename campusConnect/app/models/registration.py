"""
CampusConnect - Registration Model
=====================================
Represents a student's registration for an event.

Key DBMS Concepts:
  - Composite UNIQUE constraint on (student_id, event_id) prevents
    a student from registering twice for the same event
  - Foreign keys with CASCADE DELETE so registrations are cleaned up
    when event or student is deleted
  - Index on status for fast admin filtering

Transaction Flow:
  BEGIN TRANSACTION
    → Check available_seats > 0
    → INSERT INTO registrations
    → UPDATE events SET available_seats = available_seats - 1
    → INSERT INTO notifications
  COMMIT  (or ROLLBACK on any failure)
"""

from datetime import datetime
from ..extensions import db


class Registration(db.Model):
    """
    Registration entity.
    Junction table between Students and Events with additional metadata.

    Composite key: (student_id, event_id) enforces one-registration rule.
    Status workflow: pending → approved → attended
                  or pending → rejected
                  or approved → cancelled
    """

    __tablename__ = "registrations"

    # Composite unique constraint: one student per event
    # Index on status for admin dashboard filtering
    __table_args__ = (
        db.UniqueConstraint("student_id", "event_id",
                            name="uq_student_event"),
        db.Index("idx_reg_status", "status"),
        db.Index("idx_reg_student", "student_id"),
        db.Index("idx_reg_event", "event_id"),
    )

    # ------------------------------------------------------------------
    # Primary Key
    # ------------------------------------------------------------------
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # ------------------------------------------------------------------
    # Foreign Keys (CASCADE DELETE for referential integrity)
    # When event is deleted → remove its registrations automatically
    # When student is deleted → remove their registrations automatically
    # ------------------------------------------------------------------
    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="FK to students table"
    )
    event_id = db.Column(
        db.Integer,
        db.ForeignKey("events.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="FK to events table"
    )

    # ------------------------------------------------------------------
    # Status
    # Values: 'pending', 'approved', 'rejected', 'cancelled', 'attended'
    # ------------------------------------------------------------------
    status = db.Column(db.String(20), nullable=False, default="pending",
                       index=True,
                       comment="Registration workflow status")

    # ------------------------------------------------------------------
    # Additional fields
    # ------------------------------------------------------------------
    remarks = db.Column(db.Text, nullable=True,
                        comment="Admin notes for approval/rejection reason")
    registered_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False,
                               comment="When the student submitted registration")
    approved_at = db.Column(db.DateTime, nullable=True,
                            comment="When admin approved the registration")
    cancelled_at = db.Column(db.DateTime, nullable=True,
                             comment="When student/admin cancelled")

    # ------------------------------------------------------------------
    # Attendance is managed via separate Attendance table
    # This flag is denormalized here for quick query performance
    # ------------------------------------------------------------------
    attendance_marked = db.Column(db.Boolean, default=False, nullable=False,
                                  comment="Quick flag - full record in attendance table")

    def __repr__(self):
        return f"<Registration Student:{self.student_id} Event:{self.event_id} [{self.status}]>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "student_id": self.student_id,
            "event_id": self.event_id,
            "status": self.status,
            "registered_at": self.registered_at.isoformat(),
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
        }
