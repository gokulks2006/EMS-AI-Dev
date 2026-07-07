"""
CampusConnect - CLI Manager
=============================
Provides CLI commands using Flask-Migrate and custom commands
registered in app/__init__.py.

Usage:
  python manage.py db init
  python manage.py db migrate -m "message"
  python manage.py db upgrade
  python manage.py seed-db
"""

import os
from app import create_app
from app.extensions import db

config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    from flask.cli import FlaskGroup
    cli = FlaskGroup(create_app=lambda: app)
    cli()

