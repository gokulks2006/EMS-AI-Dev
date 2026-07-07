"""
CampusConnect - Department Model
==================================
Represents a college department (e.g., CS, ECE, Mechanical).
Students and events belong to departments.

Normalization Note:
  - Department data is separated into its own table (1NF/2NF/3NF)
  - No repeating groups, no partial dependencies, no transitive dependencies
"""

from ..extensions import db
from datetime import datetime


class Department(db.Model):
    """
    Department entity.
    Represents an academic department in the college.

    Relationships:
      - One department has many students (one-to-many)
      - One department can host many events (one-to-many)
    """

    __tablename__ = "departments"

    # ------------------------------------------------------------------
    # Primary Key
    # ------------------------------------------------------------------
    id = db.Column(db.Integer, primary_key=True, autoincrement=True,
                   comment="Unique department identifier")

    # ------------------------------------------------------------------
    # Department Attributes (All NOT NULL to maintain data integrity)
    # ------------------------------------------------------------------
    name = db.Column(db.String(100), nullable=False, unique=True,
                     comment="Full department name e.g. Computer Science")

    code = db.Column(db.String(10), nullable=False, unique=True,
                     comment="Short code e.g. CS, ECE, MECH")

    description = db.Column(db.Text, nullable=True,
                            comment="Optional department description")

    head_of_dept = db.Column(db.String(100), nullable=True,
                             comment="Name of the HOD")

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False,
                           comment="When the department record was created")

    # ------------------------------------------------------------------
    # Relationships (lazy='dynamic' for efficient large queries)
    # ------------------------------------------------------------------
    students = db.relationship("Student", backref="department",
                               lazy="dynamic", cascade="all, delete-orphan")

    events = db.relationship("Event", backref="department",
                             lazy="dynamic")

    def __repr__(self):
        """String representation for debugging."""
        return f"<Department {self.code}: {self.name}>"

    def to_dict(self):
        """Serialize department to dictionary for JSON API responses."""
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "head_of_dept": self.head_of_dept,
        }
