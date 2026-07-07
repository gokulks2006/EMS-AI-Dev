"""
CampusConnect - Student Model
================================
"""

from datetime import datetime
from flask_login import UserMixin
from ..extensions import db, bcrypt, login_manager

class Student(UserMixin, db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    roll_number = db.Column(db.String(20), unique=True, nullable=False)

    registrations = db.relationship("Registration", backref="student", lazy="dynamic", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        password = kwargs.pop("password", None)
        super(Student, self).__init__(**kwargs)
        if password:
            self.set_password(password)

    def set_password(self, password: str) -> None:
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def get_id(self) -> str:
        return f"s_{self.id}"

    def __repr__(self):
        return f"<Student {self.email}>"


@login_manager.user_loader
def load_user(user_id: str):
    if user_id.startswith("a_"):
        from .admin import Admin
        from ..extensions import db
        return db.session.get(Admin, int(user_id[2:]))
    elif user_id.startswith("s_"):
        from ..extensions import db
        return db.session.get(Student, int(user_id[2:]))
    return None
