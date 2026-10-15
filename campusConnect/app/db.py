"""
CampusConnect - Pure SQL Database Connection Manager
=====================================================
Replaces Flask-SQLAlchemy with a thin PyMySQL wrapper.

Design:
  - One persistent connection pool is NOT used here for simplicity.
  - Each request gets a connection from PyMySQL, used inside a with-block,
    and closed automatically via Flask's teardown_appcontext.
  - All SQL is written explicitly — no ORM, no query builder.

Usage in routes:
    from app.db import get_db

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM students WHERE id = %s", (student_id,))
        row = cur.fetchone()
"""

import pymysql
import pymysql.cursors
from flask import g, current_app


def get_db() -> pymysql.connections.Connection:
    """
    Return the request-scoped database connection.
    Creates one if it doesn't exist yet.
    The connection is stored on Flask's 'g' object so it's reused
    within the same request and automatically closed at teardown.
    """
    if "db" not in g:
        cfg = current_app.config
        g.db = pymysql.connect(
            host=cfg["DB_HOST"],
            port=int(cfg["DB_PORT"]),
            user=cfg["DB_USER"],
            password=cfg["DB_PASSWORD"],
            database=cfg["DB_NAME"],
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,           # explicit commit/rollback
            connect_timeout=10,
        )
    return g.db


def close_db(e=None) -> None:
    """Close the database connection at end of request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db_teardown(app) -> None:
    """Register the teardown hook so connections are closed automatically."""
    app.teardown_appcontext(close_db)


# ---------------------------------------------------------------------------
# Schema helpers (used by manage.py instead of flask-migrate)
# ---------------------------------------------------------------------------

CREATE_TABLES_SQL = """
-- Admins table
CREATE TABLE IF NOT EXISTS admins (
    id            INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    email         VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    INDEX idx_admin_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Students table
CREATE TABLE IF NOT EXISTS students (
    id            INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
    first_name    VARCHAR(50)  NOT NULL,
    last_name     VARCHAR(50)  NOT NULL,
    email         VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    roll_number   VARCHAR(20)  NOT NULL UNIQUE,
    is_active     TINYINT(1)   NOT NULL DEFAULT 1,
    INDEX idx_student_email (email),
    INDEX idx_student_roll  (roll_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Events table
CREATE TABLE IF NOT EXISTS events (
    id              INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
    title           VARCHAR(200) NOT NULL,
    description     TEXT         NOT NULL,
    venue           VARCHAR(200) NOT NULL,
    event_date      DATETIME     NOT NULL,
    total_seats     INT          NOT NULL,
    available_seats INT          NOT NULL,
    status          VARCHAR(20)  NOT NULL DEFAULT 'draft',
    INDEX idx_event_date   (event_date),
    INDEX idx_event_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Registrations table
CREATE TABLE IF NOT EXISTS registrations (
    id                INT         NOT NULL AUTO_INCREMENT PRIMARY KEY,
    student_id        INT         NOT NULL,
    event_id          INT         NOT NULL,
    status            VARCHAR(20) NOT NULL DEFAULT 'pending',
    remarks           TEXT,
    registered_at     DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    approved_at       DATETIME,
    cancelled_at      DATETIME,
    attendance_marked TINYINT(1)  NOT NULL DEFAULT 0,
    UNIQUE KEY uq_student_event (student_id, event_id),
    INDEX idx_reg_status  (status),
    INDEX idx_reg_student (student_id),
    INDEX idx_reg_event   (event_id),
    CONSTRAINT fk_reg_student FOREIGN KEY (student_id)
        REFERENCES students(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_reg_event   FOREIGN KEY (event_id)
        REFERENCES events(id)   ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""


def create_tables(conn: pymysql.connections.Connection) -> None:
    """Execute CREATE TABLE IF NOT EXISTS statements to set up the schema."""
    with conn.cursor() as cur:
        for statement in CREATE_TABLES_SQL.strip().split(";"):
            stmt = statement.strip()
            if stmt:
                cur.execute(stmt)
    conn.commit()
    print("[SUCCESS] Tables created (or already existed).")


def drop_tables(conn: pymysql.connections.Connection) -> None:
    """Drop all application tables (dev/reset use only)."""
    with conn.cursor() as cur:
        cur.execute("SET FOREIGN_KEY_CHECKS = 0")
        for table in ("registrations", "events", "students", "admins"):
            cur.execute(f"DROP TABLE IF EXISTS {table}")
        cur.execute("SET FOREIGN_KEY_CHECKS = 1")
    conn.commit()
    print("[SUCCESS] All tables dropped.")
