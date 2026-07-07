"""
CampusConnect - Event Model
==============================
Represents a college event with basic CRUD functionality.
"""

from datetime import datetime, timezone
from ..extensions import db

class Event(db.Model):
    """
    Event entity.
    Central entity of the system - students register for events.
    """
    __tablename__ = "events"

    # ------------------------------------------------------------------
    # Primary Key
    # ------------------------------------------------------------------
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # ------------------------------------------------------------------
    # Event Details
    # ------------------------------------------------------------------
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    venue = db.Column(db.String(200), nullable=False)
    event_date = db.Column(db.DateTime, nullable=False)

    # ------------------------------------------------------------------
    # Capacity Management
    # ------------------------------------------------------------------
    total_seats = db.Column(db.Integer, nullable=False)
    # Event publication status (e.g., 'draft', 'published')
    status = db.Column(db.String(20), nullable=False, default='draft')
    available_seats = db.Column(db.Integer, nullable=False)

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    registrations = db.relationship("Registration", backref="event",
                                    lazy="dynamic", cascade="all, delete-orphan")

    @property
    def is_registration_open(self) -> bool:
        """Check if event is accepting registrations."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        return (
            self.event_date > now
            and self.available_seats > 0
        )

    def __repr__(self):
        return f"<Event '{self.title}' on {self.event_date.date()}>"

    def to_dict(self) -> dict:
        """Serialize event for JSON API responses."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "venue": self.venue,
            "event_date": self.event_date.isoformat(),
            "total_seats": self.total_seats,
            "available_seats": self.available_seats,
        }
