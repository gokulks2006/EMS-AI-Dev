# CampusConnect - College Event Management System

![CampusConnect Logo](docs/images/logo.png)

CampusConnect is a production-ready, full-stack College Event Management System designed for students and administrators to streamline the process of discovering, registering, and managing college events.

## Features

**For Students:**
* **Browse Events:** View upcoming workshops, seminars, cultural fests, and sports events.
* **Registration:** One-click registration for events.
* **Dashboard:** Track upcoming registered events, attendance history, and download certificates.
* **Notifications:** Receive updates on event approvals, cancellations, and certificate issuances.

**For Administrators:**
* **Event Management:** Create, edit, and cancel events. Set capacity limits.
* **Registration Management:** Approve or reject student registrations.
* **Attendance Tracking:** Mark attendance for registered students.
* **Certificate Generation:** Automatically issue verifiable certificates to attendees.
* **Reports:** Generate CSV and PDF reports for event participation.
* **Audit Logs:** Full system audit trail for security.

## Technology Stack

* **Backend:** Python 3.12+, Flask, SQLAlchemy ORM, Flask-Login, Flask-WTF, Flask-Migrate
* **Frontend:** HTML5, CSS3, Vanilla JavaScript, Bootstrap 5 (Custom Themed), Jinja2
* **Database:** MySQL (SQLite for development/testing)
* **Security:** CSRF Protection, Bcrypt Password Hashing, SQL Injection Prevention (ORM)

## Installation and Setup

### Prerequisites
* Python 3.12 or higher
* MySQL Server (if using MySQL for production)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/CampusConnect.git
   cd CampusConnect
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**
   Create a `.env` file in the root directory based on `.env.example`:
   ```env
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=your-secure-secret-key
   DATABASE_URL=sqlite:///campus_connect.db
   ```

5. **Initialize the Database**
   Run the custom CLI commands to setup the database schemas and seed initial test data:
   ```bash
   python manage.py db upgrade
   python manage.py seed-db
   ```

6. **Run the Application**
   ```bash
   python run.py
   ```
   Access the application at `http://127.0.0.1:5000/`.

## Testing

The project uses `pytest` and `playwright` for automated testing.

To run the test suite:
```bash
# Run unit tests and browser tests
pytest

# To view print statements during testing
pytest -s -v
```

## Architecture

The system is built using the **Model-View-Controller (MVC)** architectural pattern via Flask's Application Factory pattern and Blueprints.

* `app/models/`: SQLAlchemy Database Models
* `app/routes/`: Flask Blueprints (Controllers)
* `app/templates/`: Jinja2 HTML Templates (Views)
* `app/static/`: CSS, JS, and image assets

## License
MIT License.
