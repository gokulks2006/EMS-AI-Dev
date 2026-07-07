# Software Requirements Specification (SRS)
## CampusConnect - College Event Management System

### 1. Introduction
#### 1.1 Purpose
The purpose of this document is to define the software requirements for the CampusConnect College Event Management System. This system facilitates the creation, management, and participation in college events.

#### 1.2 Scope
CampusConnect is a web-based application designed for colleges and universities. It allows administrators to create events, manage registrations, track attendance, and issue certificates. Students can view events, register, track their attendance history, and download certificates.

### 2. Overall Description
#### 2.1 User Characteristics
*   **Students:** End-users who browse events, register, and receive certificates. They require an intuitive, mobile-responsive interface.
*   **Administrators/Organizers:** Faculty or designated student coordinators who manage the events. They require tools for tracking, reporting, and managing participants.

#### 2.2 Operating Environment
*   **Backend:** Python/Flask running on a WSGI server (e.g., Gunicorn).
*   **Database:** MySQL Server (Version 8.0+).
*   **Frontend:** Modern web browsers (Chrome, Firefox, Safari, Edge).

### 3. System Features
#### 3.1 Authentication & Authorization
*   **REQ-AUTH-1:** The system shall allow students to register for an account using their college email and roll number.
*   **REQ-AUTH-2:** Passwords must be hashed using bcrypt.
*   **REQ-AUTH-3:** Administrators and Students shall have distinct login portals and dashboards.

#### 3.2 Event Management (Admin)
*   **REQ-EM-1:** Administrators can create, update, and delete events.
*   **REQ-EM-2:** Events must have a title, description, date, venue, capacity, and category.
*   **REQ-EM-3:** The system must prevent deletion of events that have active registrations (soft delete or cancellation).

#### 3.3 Registration System (Student)
*   **REQ-REG-1:** Students can view a catalog of upcoming events.
*   **REQ-REG-2:** Students can register for an event with a single click.
*   **REQ-REG-3:** The system must enforce event capacity limits using atomic database transactions (`with_for_update`) to prevent overbooking.

#### 3.4 Attendance & Certificates
*   **REQ-ATT-1:** Admins can mark attendance for registered students.
*   **REQ-ATT-2:** Upon marking attendance, the system shall automatically generate a unique certificate record for the student.
*   **REQ-ATT-3:** Students can download their certificates in PDF format.

#### 3.5 Reporting & Auditing
*   **REQ-REP-1:** The system shall provide an audit log tracking all administrative actions (login, event creation, registration approval).
*   **REQ-REP-2:** Admins can export registration and attendance data.

### 4. Non-Functional Requirements
#### 4.1 Security
*   All forms must implement CSRF protection.
*   Input validation must be performed on both client and server sides to prevent XSS and SQL Injection.
*   Admin routes must be strictly protected by role-based access control.

#### 4.2 Performance
*   Page load times should not exceed 2 seconds on a standard broadband connection.
*   The database must be normalized (3NF) to ensure data integrity and query efficiency.

#### 4.3 UI/UX Design
*   The interface must follow modern design aesthetics, featuring responsive layouts, smooth micro-animations, and a unified color scheme.
*   Dark mode support must be implemented and persisted across sessions using localStorage.
