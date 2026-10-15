# 🗺️ From Zero to CampusConnect — Your 5-Day Developer Roadmap
### (Oct 15 → Oct 20) | You already know Python, HTML, SQL — you're closer than you think!

> **Mindset first:** Your brother's app is not magic. It's just small, simple things stacked on top of each other. You'll understand every single line by Day 5. Let's go.

---

## 🛠️ FIRST: Install These Tools RIGHT NOW (30 mins)

Before anything — set up your workspace. Do this today.

| Tool | What it's for | Download |
|------|--------------|---------|
| **VS Code** | Write your code | https://code.visualstudio.com |
| **Python 3.12** | Run your code | https://www.python.org/downloads |
| **DB Browser for SQLite** | **See your database visually** (like Excel for your DB) | https://sqlitebrowser.org |
| **MySQL Workbench** | See MySQL database visually (for later) | https://dev.mysql.com/downloads/workbench |
| **Git** | Save your work versions | https://git-scm.com |

### 👁️ How to VIEW your SQL database visually (DB Browser for SQLite):
1. Open **DB Browser for SQLite**
2. Click **"Open Database"** → go to your CampusConnect project folder → `instance/` folder → open `campus_connect.db`
3. Click the **"Browse Data"** tab at the top
4. Select any table (students, events, registrations) from the dropdown
5. **You can now see all your data like an Excel sheet!**
6. To run SQL manually: click **"Execute SQL"** tab → type `SELECT * FROM students;` → press ▶

> For MySQL Workbench: Open it → click "+" to add connection → hostname: `localhost`, user: `root`, password: yours → Connect → you'll see all your databases on the left panel.

---

## 📅 THE 5-DAY PLAN

---

## DAY 1 — "What is Flask? How does a website actually work?" 
**⏰ Time needed: 4-5 hours**

### 🎯 Goal: Understand the request-response cycle. Build your first Flask page.

### 📺 Watch These (in order):
1. **"Python Flask Tutorial for Beginners"** by Corey Schafer — YouTube  
   → Watch: Part 1 and Part 2 only (about 1 hour total)  
   → Search: `Corey Schafer Flask Tutorial`

2. **"How the Internet Works in 5 Minutes"** — YouTube  
   → Search: `how the internet works in 5 minutes Aaron`

### 📖 Understand These 3 Concepts First:

**Concept 1: The Request-Response Cycle**
```
You type google.com → Browser sends REQUEST to Google's server
                    → Google's server sends back RESPONSE (HTML page)
                    → Browser shows you the page
```
Your CampusConnect does the EXACT same thing. Flask IS the server.

**Concept 2: What Flask does**
```python
# This is literally all Flask is at its core:
from flask import Flask
app = Flask(__name__)

@app.route("/")          # When someone visits "/"
def home():              # Run this function
    return "Hello!"      # Send this back to browser
```

**Concept 3: What a route is**
- `/` = home page
- `/student/dashboard` = student dashboard page
- `/admin/events` = admin events page
- Each URL maps to one Python function — that's it.

### 🔨 Mini Project — Day 1:
Build a **1-page Flask app** from scratch:

```python
# Save as: my_app.py
from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>Hello! I am learning Flask!</h1>"

@app.route("/about")
def about():
    return "<h1>My name is [Your Name]</h1>"

if __name__ == "__main__":
    app.run(debug=True)
```

Run it:
```bash
pip install flask
python my_app.py
```
Open browser → `http://127.0.0.1:5000` → You made a website! 🎉

### ✅ Day 1 Checklist:
- [ ] Installed all tools
- [ ] Watched Corey Schafer Flask Part 1 & 2
- [ ] Built and ran your first Flask page
- [ ] Understood what a "route" is

---

## DAY 2 — "HTML Templates + Connecting Python to HTML"
**⏰ Time needed: 4-5 hours**

### 🎯 Goal: Make Flask serve real HTML pages. Pass data from Python to HTML.

### 📺 Watch:
- Corey Schafer Flask — **Part 3 and Part 4** (Templates)
- Search: `Jinja2 template tutorial beginner`

### The Big Idea: Jinja2 Templates
In your CampusConnect, every page in `app/templates/` is a **Jinja2 template**. It's just HTML with special Python-like tags:

```html
<!-- Normal HTML you already know -->
<h1>Events</h1>

<!-- Jinja2: Loop through a list Python gave you -->
{% for event in events %}
    <p>{{ event.title }}</p>   <!-- Show event title -->
{% endfor %}

<!-- Jinja2: Show something only if logged in -->
{% if current_user %}
    <p>Welcome, {{ current_user.name }}!</p>
{% endif %}
```

Python sends data TO the HTML like this:
```python
@app.route("/events")
def events():
    my_events = ["Hackathon", "Sports Day", "Cultural Fest"]
    return render_template("events.html", events=my_events)
    #                                     ↑ Python list goes to HTML template
```

### 🔨 Mini Project — Day 2:
Build a **2-page app with real HTML templates**:

**File structure:**
```
my_app/
├── app.py
└── templates/
    ├── home.html
    └── events.html
```

```python
# app.py
from flask import Flask, render_template
app = Flask(__name__)

events = [
    {"title": "Hackathon", "date": "Nov 1"},
    {"title": "Sports Day", "date": "Nov 5"},
]

@app.route("/")
def home():
    return render_template("home.html", event_count=len(events))

@app.route("/events")
def events_page():
    return render_template("events.html", events=events)
```

```html
<!-- templates/events.html -->
<!DOCTYPE html>
<html>
<body>
    <h1>All Events</h1>
    {% for event in events %}
        <div>
            <h3>{{ event.title }}</h3>
            <p>Date: {{ event.date }}</p>
        </div>
    {% endfor %}
</body>
</html>
```

### ✅ Day 2 Checklist:
- [ ] Understand what Jinja2 does
- [ ] Can pass a Python list to an HTML template
- [ ] Built a 2-page app showing a list of events

---

## DAY 3 — "Databases: Connect Flask to SQLite/MySQL"
**⏰ Time needed: 5-6 hours — Most important day!**

### 🎯 Goal: Store data in a real database. Read and write from Python.

### 📺 Watch:
- Corey Schafer Flask — **Part 4 and Part 5** (Database with SQLAlchemy)
- Search: `SQLAlchemy Flask beginners`

### The Big Idea: SQLAlchemy (ORM)

You know SQL. You know how to write:
```sql
INSERT INTO students (name, email) VALUES ('John', 'john@college.edu');
SELECT * FROM students WHERE id = 1;
```

SQLAlchemy lets you write the SAME THING but in Python:
```python
# Instead of SQL INSERT:
new_student = Student(name="John", email="john@college.edu")
db.session.add(new_student)
db.session.commit()

# Instead of SQL SELECT:
student = Student.query.filter_by(id=1).first()
print(student.name)  # prints "John"
```

**A "Model" is just a Python class that represents a database table:**
```python
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Student(db.Model):          # This = students table in MySQL
    __tablename__ = "students"
    
    id = db.Column(db.Integer, primary_key=True)      # id column
    name = db.Column(db.String(100), nullable=False)   # name column
    email = db.Column(db.String(120), unique=True)     # email column (must be unique)
```

### 🔨 Mini Project — Day 3:
Build an app where you can **add and view events from a database**:

```python
# app.py
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///events.db"
db = SQLAlchemy(app)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    
with app.app_context():
    db.create_all()  # Creates the database file + tables

@app.route("/")
def home():
    all_events = Event.query.all()  # SELECT * FROM events
    return render_template("home.html", events=all_events)

@app.route("/add", methods=["POST"])
def add_event():
    title = request.form["title"]          # Get data from HTML form
    new_event = Event(title=title)         # Create Python object
    db.session.add(new_event)              # Prepare to save
    db.session.commit()                    # Actually save to database
    return redirect("/")
```

**After running this** → open DB Browser for SQLite → open `events.db` → you'll SEE your data appear! 

### ✅ Day 3 Checklist:
- [ ] Understand what SQLAlchemy is and why we use it
- [ ] Can create a Model (Python class = database table)
- [ ] Can INSERT data (db.session.add + commit)
- [ ] Can SELECT data (Model.query.all())
- [ ] Viewed the database in DB Browser for SQLite ✓

---

## DAY 4 — "Login System + Two Types of Users"
**⏰ Time needed: 5-6 hours**

### 🎯 Goal: Add login/logout. Make admin pages that only admins can see.

### 📺 Watch:
- Corey Schafer Flask — **Part 6, 7, 8** (Login with Flask-Login)
- Search: `Flask-Login tutorial beginner`

### The Big Idea: Sessions and Authentication

When you log in to any website:
1. You send your email + password
2. The server checks the database
3. If correct → server creates a **"session"** (like a wristband at a concert)
4. Every page you visit → Flask checks "do you have a wristband?"

**Flask-Login does all of this for you automatically:**

```python
from flask_login import login_user, logout_user, login_required, current_user

@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]
    
    user = Student.query.filter_by(email=email).first()
    if user and user.password == password:  # (we'll use bcrypt later)
        login_user(user)                     # Flask gives them a "session wristband"
        return redirect("/dashboard")
    return "Wrong password!"

@app.route("/dashboard")
@login_required              # ← This BLOCKS the page if not logged in!
def dashboard():
    return f"Welcome {current_user.name}!"  # current_user = logged-in user
```

### Password Hashing — Why It Matters:
```python
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()

# When user REGISTERS — never store plain password!
hashed = bcrypt.generate_password_hash("mypassword123")
# Stored in DB: "$2b$12$X3jKs..." (unreadable garbage — safe!)

# When user LOGS IN — check the hash:
bcrypt.check_password_hash(hashed, "mypassword123")  # → True
bcrypt.check_password_hash(hashed, "wrongpassword")  # → False
```

### 🔨 Mini Project — Day 4:
Add **login + logout** to your Day 3 project. Only logged-in users can add events.

### ✅ Day 4 Checklist:
- [ ] Understand what a "session" is
- [ ] Can build a login form that checks the database
- [ ] `@login_required` works — logged-out users get redirected
- [ ] Understand why we hash passwords

---

## DAY 5 — "Forms + Blueprints = Structure Like CampusConnect"
**⏰ Time needed: 5 hours**

### 🎯 Goal: Organise your code into folders like CampusConnect. Add proper forms.

### The Big Idea: Blueprints (Folders for Routes)

Right now your code is one big `app.py` file. CampusConnect splits routes into separate files:

```
app/
├── routes/
│   ├── auth.py      ← login/logout routes
│   ├── student.py   ← student dashboard, register for event
│   └── admin.py     ← admin panel, create events
```

Each file uses a **Blueprint** — think of it as a "mini Flask app" that gets plugged in:

```python
# routes/student.py
from flask import Blueprint
student_bp = Blueprint("student", __name__, url_prefix="/student")

@student_bp.route("/dashboard")    # = /student/dashboard
def dashboard():
    return "Student Dashboard"
```

```python
# app/__init__.py — plug all blueprints together
from .routes.student import student_bp
app.register_blueprint(student_bp)
```

### 🔨 Final Mini Project — Day 5:
Restructure your app into the Blueprint pattern. Your folder should look like:
```
mini_campusconnect/
├── run.py
└── app/
    ├── __init__.py
    ├── models.py
    └── routes/
        ├── auth.py
        └── student.py
```

---

## 🏗️ NOW BUILD CAMPUSCONNECT — In This Exact Order:

> After Day 5 of study, spend any remaining time building. Use this build order:

| Order | What to Build | File to Look At in Real Project |
|-------|--------------|-------------------------------|
| 1 | Create project folder structure + run.py | `run.py` |
| 2 | `app/__init__.py` — Flask factory + extensions | `app/__init__.py` |
| 3 | `app/models/student.py` — Student table | `app/models/student.py` |
| 4 | `app/models/event.py` — Event table | `app/models/event.py` |
| 5 | `app/models/registration.py` — Registration table | `app/models/registration.py` |
| 6 | `app/routes/auth.py` — Register + Login | `app/routes/auth.py` |
| 7 | `app/templates/auth/` — Login/Register HTML | `app/templates/auth/` |
| 8 | `app/routes/student.py` — Dashboard + Event list | `app/routes/student.py` |
| 9 | `app/routes/admin.py` — Admin panel | `app/routes/admin.py` |
| 10 | Test everything end-to-end | Run `python run.py` |

---

## 📚 Your Study Resources (All Free)

| Resource | What for | Link |
|----------|---------|------|
| **Corey Schafer Flask Series** | Main learning | YouTube search |
| **Flask Official Docs** | Reference | https://flask.palletsprojects.com |
| **SQLAlchemy Docs** | Database reference | https://flask-sqlalchemy.palletsprojects.com |
| **W3Schools SQL** | SQL revision | https://w3schools.com/sql |
| **Bootstrap 5 Docs** | Make pages look good | https://getbootstrap.com |

---

## 🔑 The 10 Concepts You MUST Understand Before Day 20

Learn these in order. Each one unlocks the next.

```
1. HTTP Request/Response      → What happens when you click a button
2. Flask Routes (@app.route)  → Which Python function handles which URL  
3. Jinja2 Templates           → Python variables inside HTML
4. SQLAlchemy Models          → Python class = Database table
5. db.session.add/commit      → How data gets saved to MySQL
6. Flask-Login                → How login/logout/sessions work
7. Bcrypt Password Hashing    → Why passwords are never stored plain
8. Flask Blueprints           → How to organise routes into folders
9. CSRF Protection            → Hidden form tokens to block fake requests
10. Foreign Keys              → How students LINK to registrations LINK to events
```

---

## 💪 Final Motivation

> You're not starting from zero — you know Python, HTML, and SQL. That's literally 70% of what this app needs. The other 30% is just Flask connecting all three together.
>
> In 5 days you'll understand every single file in your brother's project. Not because you memorised it — because you **built the same thing yourself**.
>
> **Start with Day 1 right now. Don't skip ahead. The order matters.**
