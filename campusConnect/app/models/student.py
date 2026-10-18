"""
CampusConnect - Student Model (Pure SQL)
==========================================
Plain Python class that mirrors the `students` table.
No ORM — all database interaction happens through raw SQL.
"""

from flask_login import UserMixin
from flask_bcrypt import Bcrypt

_bcrypt = Bcrypt()


class Student(UserMixin):
    """
    Represents a row from the `students` table.
    Attributes map 1-to-1 to table columns.
    """

    def __init__(
        self,
        id: int,
        first_name: str,
        last_name: str,
        email: str,
        password_hash: str = "",
        roll_number: str = None,
        is_active: bool = True,
        department_id: int = None,
        department_name: str = None,
        department_code: str = None,
    ):
        self.id              = id
        self.first_name      = first_name
        self.last_name       = last_name
        self.email           = email
        self.password_hash   = password_hash
        self.roll_number     = roll_number
        self._is_active      = bool(is_active)
        self.department_id   = department_id
        self.department_name = department_name
        self.department_code = department_code

    # ------------------------------------------------------------------
    # Flask-Login interface
    # ------------------------------------------------------------------

    def get_id(self) -> str:
        """Prefix 's_' to distinguish student sessions from admin sessions."""
        return f"s_{self.id}"

    @property
    def is_active(self) -> bool:
        return self._is_active

    # ------------------------------------------------------------------
    # Convenience properties
    # ------------------------------------------------------------------

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def department(self) -> str:
        return self.department_name or ""

    # ------------------------------------------------------------------
    # Password helpers
    # ------------------------------------------------------------------

    @staticmethod
    def hash_password(password: str) -> str:
        """Return a bcrypt hash for the given plaintext password."""
        return _bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str) -> bool:
        """Verify a plaintext password against the stored hash."""
        return _bcrypt.check_password_hash(self.password_hash, password)

    # ------------------------------------------------------------------
    # SQL helpers — build Student from a DB row dict
    # ------------------------------------------------------------------

    @classmethod
    def from_row(cls, row: dict) -> "Student":
        """Construct a Student instance from a pymysql DictCursor row."""
        return cls(
            id=row["id"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            email=row["email"],
            password_hash=row.get("password_hash", ""),
            roll_number=row.get("roll_number"),
            is_active=row.get("is_active", 1),
            department_id=row.get("department_id"),
            department_name=row.get("department_name"),
            department_code=row.get("department_code"),
        )

    def __repr__(self):
        return f"<Student {self.email}>"
