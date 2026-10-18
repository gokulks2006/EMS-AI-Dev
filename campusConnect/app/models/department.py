"""
CampusConnect - Department Model (Pure SQL)
===========================================
Plain Python class that mirrors the `departments` table.
No ORM — all database interaction happens through raw SQL.
"""


class Department:
    """
    Represents a row from the `departments` table.
    """

    def __init__(self, id: int, name: str, code: str):
        self.id   = id
        self.name = name
        self.code = code

    @classmethod
    def from_row(cls, row: dict) -> "Department":
        """Construct a Department instance from a pymysql DictCursor row."""
        return cls(
            id=row["id"],
            name=row["name"],
            code=row.get("code", ""),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
        }

    def __repr__(self):
        return f"<Department {self.code}: {self.name}>"
