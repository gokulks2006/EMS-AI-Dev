"""
CampusConnect - Helper Functions
==================================
Utility functions for the application.
"""
import re
from markupsafe import escape

def sanitize_input(value: str) -> str:
    """
    Sanitize string input to prevent basic XSS and normalize whitespace.
    """
    if not value:
        return ""
    
    sanitized = str(escape(value))
    sanitized = " ".join(sanitized.split())
    return sanitized
