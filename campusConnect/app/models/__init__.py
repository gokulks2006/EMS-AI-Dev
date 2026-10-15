"""
CampusConnect - Models Package (Pure SQL)
==========================================
Exports all plain-Python model classes.
These classes have NO ORM dependency — they are simple data containers
populated from pymysql DictCursor rows via each class's from_row() method.
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
