# TaskMate — Django Notes App


## Table of Contents

- [Tech Stack](#tech-stack)
- [Authentication — How Session Login Works](#authentication--how-session-login-works)
- [Database — SQLite (Default) & PostgreSQL](#database--sqlite-default--postgresql)
- [Features](#features)
- [Project Structure](#project-structure)
- [Environment Variables](#environment-variables)
- [Quick Start (Local Development)](#quick-start-local-development)
- [Common Errors & Fixes](#common-errors--fixes)

---


## Features

- **Protected Dashboard** — `@login_required` on all dashboard views; unauthenticated users are redirected to login
- **User Registration** — creates a new `auth_user` record with a hashed password via `UserCreationForm`
- **User Login** — session-based, sets `sessionid` cookie
- **GitHub Sign-In (Optional)** — Firebase popup flow verifies an ID token server-side; Django then creates/fetches the matching user and starts a standard Django session

  ![Login page with GitHub sign-in](https://github.com/user-attachments/assets/8455deab-3ce5-446f-9e39-aa9ba86d2438)

- **Todo List** — add tasks, mark as complete (toggles `completed` boolean field), delete tasks; each task is scoped to `request.user`

  ![Todo list dashboard](https://github.com/user-attachments/assets/7d297077-9eb6-4241-bf4a-de46d3834cd0)

- ** Text Notes** — create notes with formatting; notes auto-save; each note is scoped to `request.user`; delete supported

  ![Notes dashboard](https://github.com/user-attachments/assets/f6c7cf14-859a-4c74-8f75-148665bfa8b8)


---

## Tech Stack

| Layer        | Technology                                      |
|--------------|-------------------------------------------------|
| Backend      | Django 4.x (Python 3.12)                        |
| Auth         | Django session auth + optional Firebase (GitHub)|
| Database     | SQLite (dev) / PostgreSQL via `DATABASE_URL` (prod) |
| Text    | Integrated via frontend editor in dashboard     |
| Deployment   | Railway (Gunicorn + Procfile)                   |
| Environment  | `python-dotenv` for `.env` loading              |

---

## Authentication — How Session Login Works

TaskMate uses **Django's built-in session-based authentication** — no JWT, no tokens on the client side for standard login.

### How it works step by step:

1. **User submits credentials** via `POST /accounts/login/`
2. Django's `authenticate()` function checks the submitted `username` and `password` against the `auth_user` table in the database (passwords are stored as hashed values using PBKDF2 by default — never plain text)
3. If credentials match, Django calls `login(request, user)` which:
   - Creates a new row in the `django_session` table
   - Stores the `user_id` and session metadata (encoded + signed) in that row
   - Sets a `sessionid` cookie on the browser with the session key
4. On every subsequent request, the browser sends the `sessionid` cookie automatically
5. Django's `SessionMiddleware` reads the cookie, looks up the session in `django_session`, and attaches `request.user` — so views always know who is logged in
6. The `@login_required` decorator on the dashboard view checks `request.user.is_authenticated` — if `False`, the user is redirected to `/accounts/login/`

### Logout:

- `GET /accounts/logout/` calls Django's `logout(request)`, which deletes the session row from `django_session` and clears the cookie — the user is fully logged out

### Session table:

Django manages the `django_session` table automatically. It has three columns:

```
session_key   — unique random key (set as cookie)
session_data  — base64-encoded, signed session payload
expire_date   — when the session expires (default: 2 weeks)
```

Sessions can be cleared with:
```bash
python manage.py clearsessions
```
---

## Database — SQLite (Default) & PostgreSQL

### SQLite (Development Default)

Django uses **SQLite out of the box** — no installation or configuration required. The database is a single file: `db.sqlite3`, created in the project root after running migrations.

**Default `settings.py` config:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

SQLite is perfect for local development:
- Zero setup
- File-based, easily reset (just delete `db.sqlite3`)
- Supports all Django ORM operations used in this project

**Tables created after `migrate`:**

| Table                  | Purpose                                      |
|------------------------|----------------------------------------------|
| `auth_user`            | Stores registered users (username, password hash, email) |
| `auth_permission`      | Django permission records                    |
| `django_session`       | Active login sessions (session key + data)   |
| `django_content_type`  | Framework metadata for permissions           |
| `django_admin_log`     | Admin panel action history                   |
| `django_migrations`    | Tracks which migrations have been applied    |
| `todos_todo`           | User's todo tasks                            |
| `todos_note`           | User's text notes                       |

### PostgreSQL (Production — Railway)

When deployed to Railway, a PostgreSQL service is linked and the `DATABASE_URL` environment variable is set automatically. Django switches to PostgreSQL by reading this variable (using `dj-database-url` or similar).

**Add to `settings.py` for production:**
```python
import dj_database_url
import os

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600
    )
}
```

PostgreSQL differences from SQLite to be aware of:
- Case-sensitive string comparisons
- Strict field type enforcement
- `makemigrations` + `migrate` must be re-run on every new deployment
- The `db.sqlite3` file is NOT used in production

---

---

## Project Structure

```
todoapp/
├── manage.py                     # Django CLI entry point
├── requirements.txt              # Python dependencies
├── Procfile                      # Railway: runs migrate + gunicorn
├── runtime.txt                   # Pins Python 3.12 for Railway
├── .env.example                  # Template for environment variables
├── db.sqlite3                    # Auto-created SQLite file (local only)
│
├── todoapp/                      # Core Django project package
│   ├── settings.py               # All app settings (DB, auth, installed apps)
│   ├── urls.py                   # Root URL dispatcher
│   └── wsgi.py / asgi.py         # Server entry points
│
├── accounts/                     # Auth app (register, login, logout, Firebase)
│   ├── views.py                  # register_view, login_view, logout_view, firebase_session
│   ├── urls.py                   # /accounts/* routes
│   └── templates/accounts/
│       ├── login.html
│       ├── register.html
│       └── includes/
│           └── firebase_github.html   # GitHub popup button (shown only if Firebase env vars set)
│
├── todos/                        # Main feature app (tasks + notes)
│   ├── models.py                 # Todo and Note models (ForeignKey to auth_user)
│   ├── views.py                  # dashboard_view, add_task, toggle_task, delete_task, save_note, delete_note
│   ├── urls.py                   # /todos/* routes
│   └── migrations/               # Auto-generated migration files
│
└── templates/
    ├── base.html                 # Shared layout (navbar, session user info)
    └── todos/
        └── dashboard.html        # Main authenticated view (tasks + notes UI)
```

---

## Environment Variables

Copy `.env.example` to `.env` in the project root. Django loads it on startup via `python-dotenv`.

```env
# Core Django
SECRET_KEY=your-strong-random-secret-key
DEBUG=True                          # Set False in production
ALLOWED_HOSTS=localhost,127.0.0.1   # Comma-separated

# Optional: Firebase GitHub Login (leave blank to disable GitHub button)
FIREBASE_WEB_API_KEY=
FIREBASE_AUTH_DOMAIN=
FIREBASE_PROJECT_ID=
FIREBASE_APP_ID=
FIREBASE_MESSAGING_SENDER_ID=

# Firebase Admin (server-side token verification)
# Local: path to service account JSON file
GOOGLE_APPLICATION_CREDENTIALS=/path/to/serviceAccountKey.json
# OR for Railway: paste full JSON content
FIREBASE_SERVICE_ACCOUNT_JSON=
```

**The "Continue with GitHub" button only appears when all three of these are set:**
- `FIREBASE_WEB_API_KEY`
- `FIREBASE_AUTH_DOMAIN`
- `FIREBASE_PROJECT_ID`

---

## Quick Start (Local Development)

### 1. Clone the repository
```bash
git clone https://github.com/your-username/Django-taskmanager.git
cd Django-taskmanager
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your values (at minimum, set SECRET_KEY)
```

### 5. Run migrations (creates db.sqlite3 and all tables)
```bash
python manage.py migrate
```

This runs all pending migrations including Django's built-in ones (`auth`, `sessions`, `admin`, `contenttypes`) and the app-specific ones (`todos`).

### 6. (Optional) Create a Django superuser for admin panel access
```bash
python manage.py createsuperuser
```

Access the admin at `http://127.0.0.1:8000/admin/` — useful for inspecting users, sessions, tasks, and notes directly.

### 7. Start the development server
```bash
python manage.py runserver
```

The root URL `/` redirects to `/todos/` (dashboard). If not logged in, Django redirects to `/accounts/login/`.

---

## Common Errors & Fixes

### `OperationalError: no such table: todos_todo`

**Cause:** The `todos` app migrations have not been created or applied yet. The `Todo` and `Note` tables do not exist in `db.sqlite3`.

**Fix:**
```bash
python manage.py makemigrations todos
python manage.py migrate
```

Run this whenever you:
- Set up a new local environment
- Pull changes that include new model fields
- Deploy to a new server

---

### `500 Internal Server Error` on Login or Register

**Cause:** Core Django tables (e.g., `auth_user`, `django_session`) don't exist yet.

**Fix:** Run `python manage.py migrate` before starting the server.

---


