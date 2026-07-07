"""
CampusConnect - Admin Model
==============================
"""

from flask_login import UserMixin
from ..extensions import db, bcrypt

class Admin(UserMixin, db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password: str) -> None:
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)

    def get_id(self) -> str:
        return f"a_{self.id}"

    def __repr__(self):
        return f"<Admin {self.email}>"
