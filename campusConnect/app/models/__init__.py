"""
CampusConnect - Models Package
================================
Imports all models so they're registered with SQLAlchemy when the app starts.
"""

from .admin import Admin
from .student import Student
from .event import Event
from .registration import Registration

__all__ = [
    "Admin",
    "Student",
    "Event",
    "Registration",
]
