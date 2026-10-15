"""
CampusConnect - Event Model (Pure SQL)
========================================
Plain Python class that mirrors the `events` table.
No ORM — all database interaction happens through raw SQL.
"""

from datetime import datetime, timezone


class Event:
    """
    Represents a row from the `events` table.
    Attributes map 1-to-1 to table columns.
    """

    def __init__(
        self,
        id: int,
        title: str,
        description: str,
        venue: str,
        event_date: datetime,
        total_seats: int,
        available_seats: int,
        status: str = "draft",
    ):
        self.id              = id
        self.title           = title
        self.description     = description
        self.venue           = venue
        self.event_date      = event_date
        self.total_seats     = total_seats
        self.available_seats = available_seats
        self.status          = status

    # ------------------------------------------------------------------
    # Domain logic
    # ------------------------------------------------------------------

    @property
    def is_registration_open(self) -> bool:
        """Check if event is accepting registrations."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        return self.event_date > now and self.available_seats > 0

    # ------------------------------------------------------------------
    # SQL helpers — build Event from a DB row dict
    # ------------------------------------------------------------------

    @classmethod
    def from_row(cls, row: dict) -> "Event":
        """Construct an Event instance from a pymysql DictCursor row."""
        return cls(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            venue=row["venue"],
            event_date=row["event_date"],
            total_seats=row["total_seats"],
            available_seats=row["available_seats"],
            status=row.get("status", "draft"),
        )

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
            "status": self.status,
        }

    def __repr__(self):
        return f"<Event '{self.title}' on {self.event_date.date()}>"
