"""
CampusConnect - Application Entry Point
=========================================
Runs the Flask application using the factory pattern.
Defaults to DevelopmentConfig unless FLASK_ENV is set to 'production'.
"""

import os
from app import create_app

# Use development config by default if not specified
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    # In a real production environment, use gunicorn or Waitress (for Windows)
    # e.g., waitress-serve --port=5000 run:app
    app.run(host='127.0.0.1', port=5000, debug=(config_name == 'development'))
