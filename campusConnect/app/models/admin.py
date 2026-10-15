"""
CampusConnect - Admin Model (Pure SQL)
=======================================
Plain Python class that mirrors the `admins` table.
No ORM — all database interaction happens through raw SQL in routes/seed.
"""

from flask_login import UserMixin
from flask_bcrypt import Bcrypt

_bcrypt = Bcrypt()


class Admin(UserMixin):
    """
    Represents a row from the `admins` table.
    Attributes map 1-to-1 to table columns.
    """

    def __init__(self, id: int, name: str, email: str, password_hash: str):
        self.id            = id
        self.name          = name
        self.email         = email
        self.password_hash = password_hash

    # ------------------------------------------------------------------
    # Flask-Login interface
    # ------------------------------------------------------------------

    def get_id(self) -> str:
        """Prefix 'a_' to distinguish admin sessions from student sessions."""
        return f"a_{self.id}"

    @property
    def is_active(self) -> bool:
        return True

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
    # SQL helpers — build Admin from a DB row dict
    # ------------------------------------------------------------------

    @classmethod
    def from_row(cls, row: dict) -> "Admin":
        """Construct an Admin instance from a pymysql DictCursor row."""
        return cls(
            id=row["id"],
            name=row["name"],
            email=row["email"],
            password_hash=row["password_hash"],
        )

    def __repr__(self):
        return f"<Admin {self.email}>"
