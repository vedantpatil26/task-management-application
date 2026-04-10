# ⬡ TaskMaster

> A full-stack Task Management application built for the Oritso Private Limited screening assignment.

---

## Table of Contents

1. [Overview](#1-overview)
2. [DB Design](#2-db-design)
   - [ER Diagram](#21-er-diagram)
   - [Data Dictionary](#22-data-dictionary)
   - [Indexes](#23-indexes)
   - [DB First vs Code First](#24-db-first-vs-code-first-approach)
3. [Application Structure](#3-application-structure)
4. [Frontend Structure](#4-frontend-structure)
5. [Build & Install](#5-build--install)
6. [Running the Project](#6-running-the-project)
7. [Features Implemented](#7-features-implemented)
8. [API Endpoints](#8-api-endpoints)
9. [Running Tests](#9-running-tests)

---

## 1. Overview

**TaskMaster** is a web-based Task Management application that demonstrates full CRUD (Create, Read, Update, Delete, Search) operations using the MVC (Model-View-Controller) architectural pattern.

### What is being built?

A multi-user task management system where authenticated users can:
- **Create** tasks with title, description, due date, status, and remarks
- **Read** and view all task details including full audit trail (who created/updated and when)
- **Update** any task's fields
- **Delete** tasks with confirmation
- **Search** tasks by keyword, status, and date range
- View a **dashboard** with live statistics

### Tech Stack

| Layer       | Technology                          |
|-------------|-------------------------------------|
| Language    | Python 3.10+                        |
| Framework   | Flask 3.0 (MVC pattern)            |
| Database    | PostgreSQL                          |
| ORM         | SQLAlchemy (via Flask-SQLAlchemy)   |
| Migrations  | Flask-Migrate (Alembic)             |
| Auth        | Flask-Login                         |
| Frontend    | Jinja2 templates + vanilla JS/CSS   |
| Testing     | pytest                              |
| SCM         | Git / GitHub                        |

---

## 2. DB Design

### 2.1 ER Diagram

```
┌──────────────────────────────────┐       ┌──────────────────────────────────────────────┐
│              users               │       │                    tasks                     │
├──────────────────────────────────┤       ├──────────────────────────────────────────────┤
│ PK  id           INTEGER         │◄──┐   │ PK  id                  INTEGER              │
│     username     VARCHAR(80)  UQ │   │   │     title               VARCHAR(200)         │
│     email        VARCHAR(120) UQ │   │   │     description         TEXT                 │
│     password_hash VARCHAR(256)   │   │   │     due_date            DATE                 │
│     full_name    VARCHAR(150)    │   │   │     status              ENUM(TaskStatus)     │
│     created_at   TIMESTAMP       │   │   │     remarks             TEXT                 │
│     is_active    BOOLEAN         │   │   │     created_on          TIMESTAMP            │
└──────────────────────────────────┘   │   │     last_updated_on     TIMESTAMP            │
                                       ├───│ FK  created_by_id       INTEGER → users.id   │
                                       └───│ FK  last_updated_by_id  INTEGER → users.id   │
                                           └──────────────────────────────────────────────┘

Relationships:
  users (1) ──< tasks (many) via created_by_id
  users (1) ──< tasks (many) via last_updated_by_id
```

### 2.2 Data Dictionary

#### Table: `users`

| Column        | Type         | Constraints          | Description                          |
|---------------|--------------|----------------------|--------------------------------------|
| id            | INTEGER      | PK, AUTO INCREMENT   | Unique user identifier               |
| username      | VARCHAR(80)  | NOT NULL, UNIQUE     | Login username                       |
| email         | VARCHAR(120) | NOT NULL, UNIQUE     | User email address                   |
| password_hash | VARCHAR(256) | NOT NULL             | Bcrypt-hashed password               |
| full_name     | VARCHAR(150) | NOT NULL             | Display name used in audit fields    |
| created_at    | TIMESTAMP    | NOT NULL, DEFAULT NOW| Account creation timestamp           |
| is_active     | BOOLEAN      | NOT NULL, DEFAULT TRUE| Soft-disable toggle                 |

#### Table: `tasks`

| Column              | Type         | Constraints               | Description                                      |
|---------------------|--------------|---------------------------|--------------------------------------------------|
| id                  | INTEGER      | PK, AUTO INCREMENT        | Unique task identifier                           |
| title               | VARCHAR(200) | NOT NULL                  | Task Title (required)                            |
| description         | TEXT         | NULLABLE                  | Task Description                                 |
| due_date            | DATE         | NULLABLE                  | Task Due Date                                    |
| status              | ENUM         | NOT NULL, DEFAULT PENDING | Task Status (see enum values below)              |
| remarks             | TEXT         | NULLABLE                  | Task Remarks / additional notes                  |
| created_on          | TIMESTAMP    | NOT NULL, DEFAULT NOW     | Created On — automatic timestamp on insert       |
| last_updated_on     | TIMESTAMP    | NOT NULL, AUTO-UPDATE NOW | Last Updated On — auto-updates on every change   |
| created_by_id       | INTEGER      | NOT NULL, FK → users.id   | Created By — stores User ID (name via JOIN)      |
| last_updated_by_id  | INTEGER      | NOT NULL, FK → users.id   | Last Updated By — stores User ID (name via JOIN) |

#### Enum: `TaskStatus`

| Value       | Meaning                            |
|-------------|------------------------------------|
| PENDING     | Task created but not started       |
| IN_PROGRESS | Work is currently underway         |
| COMPLETED   | Task finished                      |
| ON_HOLD     | Paused, waiting for something      |
| CANCELLED   | Task will not be done              |

### 2.3 Indexes

The following indexes are defined on the `tasks` table for query performance:

| Index Name             | Column(s)      | Rationale                                              |
|------------------------|----------------|--------------------------------------------------------|
| `idx_tasks_status`     | status         | Filter tasks by status (most common query pattern)     |
| `idx_tasks_due_date`   | due_date       | Sort and filter by due date; overdue detection         |
| `idx_tasks_created_by` | created_by_id  | Fetch tasks created by a specific user                 |
| `idx_tasks_created_on` | created_on     | Default sort column for task listing                   |
| `idx_tasks_title`      | title          | Supports partial ILIKE search on title                 |
| (implicit) PK index    | id             | Auto-created by PostgreSQL on primary key              |
| (implicit) UQ index    | username       | Auto-created by PostgreSQL on UNIQUE constraint        |
| (implicit) UQ index    | email          | Auto-created by PostgreSQL on UNIQUE constraint        |

### 2.4 DB First vs Code First Approach

**Approach used: Code First**

**Reason:** The application models are defined as Python classes using SQLAlchemy ORM. Flask-Migrate (powered by Alembic) generates SQL migration scripts automatically from the model definitions. This approach was chosen because:

1. **Single source of truth** — The model class is the definitive schema. There is no risk of drift between the Python model and the database schema.
2. **Version control friendly** — Migration files are committed to Git, giving a full, reproducible history of schema changes.
3. **Developer velocity** — Adding a column means editing the Python class, then running `flask db migrate && flask db upgrade`. No manual SQL required.
4. **Cross-DB portability** — SQLAlchemy abstracts the dialect, so the same models work against PostgreSQL, MySQL, or SQLite (e.g., for testing with SQLite in-memory).

---

## 3. Application Structure

### MVC Pattern

```
taskmaster/
├── app.py                          ← Entry point (Flask app creation)
├── config.py                       ← Config classes (Dev / Prod / Testing)
├── init_db.py                      ← DB init & seed script
├── requirements.txt
├── .env.example
│
└── app/
    ├── __init__.py                 ← App factory (create_app)
    │
    ├── models/                     ← M — MODEL layer (data + business rules)
    │   ├── __init__.py
    │   ├── user_model.py           ← User model + Flask-Login integration
    │   └── task_model.py           ← Task model with all assignment fields
    │
    ├── controllers/                ← C — CONTROLLER layer (request handling)
    │   ├── __init__.py
    │   ├── auth_controller.py      ← Register, Login, Logout routes
    │   ├── task_controller.py      ← CRUD + Search routes for tasks
    │   └── main_controller.py      ← Dashboard, home redirect
    │
    └── views/                      ← V — VIEW layer (templates + static assets)
        ├── templates/
        │   ├── base.html           ← Base layout, navbar, flash messages
        │   ├── auth/
        │   │   ├── login.html
        │   │   └── register.html
        │   ├── main/
        │   │   └── dashboard.html
        │   └── tasks/
        │       ├── list.html       ← Paginated task list with filters
        │       ├── detail.html     ← Full task detail + audit info
        │       ├── create.html     ← Create task form
        │       ├── edit.html       ← Edit task form
        │       └── search.html     ← Search with filters
        └── static/
            ├── css/style.css
            └── js/main.js
```

### Architecture Decision: SPA or MVC/MPA?

**Chosen: Standard MVC with server-side rendering (MPA — Multi-Page Application)**

**Reason:** The assignment specifically asks to demonstrate MVC pattern programming. Server-side rendering with Jinja2 templates is the most direct demonstration of the MVC pattern where:
- **Model** = SQLAlchemy ORM classes
- **View** = Jinja2 HTML templates
- **Controller** = Flask Blueprint route handlers

The application also includes a `/tasks/api/tasks` JSON endpoint demonstrating API-style output capability.

---

## 4. Frontend Structure

### What kind of frontend was used and why?

**Web page frontend (HTML/CSS/JavaScript) with Jinja2 server-side templating**

- **Jinja2** renders full HTML pages on the server. Each page is a complete HTML document, inheriting from `base.html` via Jinja2 template inheritance (`{% extends %}`).
- **Vanilla CSS** with CSS custom properties (variables) for consistent theming — no heavy CSS framework dependencies.
- **Vanilla JavaScript** (no framework) for lightweight UI enhancements: alert auto-dismiss, entrance animations, keyboard shortcuts.
- **Google Fonts** for typography: `Space Mono` (display / monospace) + `DM Sans` (body text).

**Why not React/Vue?**
The assignment emphasises MVC pattern. A full SPA would shift the controller logic into the frontend and complicate the MVC demonstration. Server-side rendering keeps the pattern clean and straightforward to evaluate.

---

## 5. Build & Install

### Prerequisites

| Requirement    | Version   | Notes                              |
|----------------|-----------|------------------------------------|
| Python         | 3.10+     | Check: `python --version`          |
| pip            | Latest    | Comes with Python                  |
| PostgreSQL     | 14+       | Must be running                    |
| Git            | Any       | For cloning the repo               |

### Environment Details

Tested on:
- **OS:** Ubuntu 22.04 LTS / macOS 14 / Windows 11 (WSL2 recommended)
- **Python:** 3.11
- **PostgreSQL:** 15

### Dependencies

All Python dependencies are in `requirements.txt`:

```
Flask==3.0.3
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.7
Flask-Login==0.6.3
psycopg2-binary==2.9.9
Werkzeug==3.0.3
python-dotenv==1.0.1
```

---

## 6. Running the Project

### Step 1 — Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/taskmaster.git
cd taskmaster
```

### Step 2 — Create a Virtual Environment

```bash
# Create venv
python -m venv venv

# Activate it
# On Linux/macOS:
source venv/bin/activate

# On Windows (CMD):
venv\Scripts\activate.bat

# On Windows (PowerShell):
venv\Scripts\Activate.ps1
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Configure Environment Variables

```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your database credentials
nano .env   # or use any text editor
```

Your `.env` should look like:

```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-random-secret-key-here

DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
DB_NAME=taskmaster_db
```

### Step 5 — Create PostgreSQL Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Inside psql:
CREATE DATABASE taskmaster_db;
\q
```

### Step 6 — Initialize Database

**Option A: Using the seed script (recommended for first run)**

```bash
python init_db.py
```

This creates all tables and populates sample data with two demo users:
- Username: `admin` / Password: `admin123`
- Username: `alice` / Password: `alice123`

**Option B: Using Flask-Migrate**

```bash
flask db init        # Only needed the very first time (creates migrations/ folder)
flask db migrate -m "Initial migration"
flask db upgrade
```

### Step 7 — Run the Application

```bash
flask run
# Or equivalently:
python app.py
```

Open your browser at: **http://localhost:5000**

---

## 7. Features Implemented

| Feature               | Route                          | Description                                               |
|-----------------------|--------------------------------|-----------------------------------------------------------|
| Register              | `GET/POST /auth/register`      | New user registration with validation                     |
| Login                 | `GET/POST /auth/login`         | Session-based authentication                              |
| Logout                | `GET /auth/logout`             | Clears session                                            |
| Dashboard             | `GET /dashboard`               | Stats overview + recent tasks                             |
| **Create** Task       | `GET/POST /tasks/create`       | Form to create a new task                                 |
| **Read** Task List    | `GET /tasks/`                  | Paginated list with status filter and sort                |
| **Read** Task Detail  | `GET /tasks/<id>`              | Full task detail with audit trail                         |
| **Update** Task       | `GET/POST /tasks/<id>/edit`    | Edit all task fields                                      |
| **Delete** Task       | `POST /tasks/<id>/delete`      | Delete with confirmation prompt                           |
| **Search** Tasks      | `GET /tasks/search`            | Search by keyword + status + date range filters           |
| JSON API              | `GET /tasks/api/tasks`         | Returns all tasks as JSON (REST style)                    |

---

## 8. API Endpoints

### REST JSON Endpoint

```
GET /tasks/api/tasks
Authorization: Session cookie (must be logged in)
```

**Sample Response:**
```json
[
  {
    "id": 1,
    "title": "Setup project repository",
    "description": "Initialize GitHub repo...",
    "due_date": "2025-04-05",
    "status": "Completed",
    "remarks": "Done.",
    "created_on": "2025-04-01T10:00:00",
    "last_updated_on": "2025-04-03T14:22:00",
    "created_by_id": 1,
    "created_by_name": "Admin User",
    "last_updated_by_id": 1,
    "last_updated_by_name": "Admin User"
  }
]
```

---

## 9. Running Tests

```bash
# Install pytest if not already installed
pip install pytest

# Run all tests
pytest tests/ -v

# Run with coverage report
pip install pytest-cov
pytest tests/ -v --cov=app --cov-report=term-missing
```

Tests cover:
- User registration and login
- Invalid login rejection
- Task creation, retrieval, update, delete
- Task search
- `is_overdue` property logic

---

## Project Author

Built as part of the Oritso Private Limited Senior Software Engineer screening assignment.

- **Architecture:** MVC (Model-View-Controller)
- **Language:** Python 3
- **Framework:** Flask
- **Database:** PostgreSQL
- **DB Approach:** Code First (SQLAlchemy ORM + Flask-Migrate)
- **Frontend:** Server-side rendered MPA (Jinja2 templates)

---

*© 2025. This project was created solely for candidate screening purposes.*
