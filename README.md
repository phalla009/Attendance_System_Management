# Attendance System Management

> A robust web-based Attendance System Management application built with Python, Flask, and SQLite.

---

## 🚀 Features

*   **User Authentication:** Secure login, registration, and role management.
*   **Attendance Tracking:** Record and monitor daily attendance records.
*   **Modular Architecture:** Organized code structure with dedicated packages for forms, models, and routes.
*   **Database Management:** Powered by SQLite and integrated with Flask-Migrate for seamless schema migrations.

---

## 🛠️ Tech Stack

*   **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-Migrate
*   **Database:** SQLite
*   **Frontend:** HTML5, CSS3, Jinja2 Templates
*   **Environment:** Virtual Environment (`venv`)

---

## 📁 Project Structure

```text
Attendance_System/
│
├── forms/            # Flask-WTF or custom form validation classes
├── instance/         # Instance-specific data (e.g., SQLite database files)
├── migrations/       # Database migration scripts (Flask-Migrate)
├── models/           # Database models and schemas
├── routes/           # Blueprint route controllers and views
├── static/           # CSS, JavaScript, and image assets
├── templates/        # HTML Jinja2 template files
├── venv/             # Python virtual environment
├── app.py            # Main Flask application entry point
├── extensions.py     # Initialized Flask extensions (DB, Migrate, etc.)
└── README.md         # Project documentation
