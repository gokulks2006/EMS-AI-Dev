"""CampusConnect - Routes Package"""
from .main import main_bp
from .auth import auth_bp
from .admin import admin_bp
from .student import student_bp

__all__ = ["main_bp", "auth_bp", "admin_bp", "student_bp"]
