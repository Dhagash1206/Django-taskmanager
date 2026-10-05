
# Features

- **Protected Dashboard** — `@login_required` on all dashboard views; unauthenticated users are redirected to login
- **User Registration** — creates a new `auth_user` record with a hashed password via `UserCreationForm`
- **User Login** — session-based, sets `sessionid` cookie
- **GitHub Sign-In** — Firebase popup flow verifies an ID token server-side; Django then creates/fetches the matching user and starts a standard Django session

- <img width="1920" height="1080" alt="Screenshot 2026-04-15 200003" src="https://github.com/user-attachments/assets/792e5b65-9773-4319-85e3-46966b56ab37" />


- **Todo Notes** — create notes with formatting; notes auto-save; each note is scoped to `request.user`; delete supported

<img width="1920" height="1080" alt="Screenshot 2026-04-15 195938" src="https://github.com/user-attachments/assets/a1443af6-f682-4ec7-9bb2-9db63e4795ff" />


- **Todo List** — add tasks, mark as complete (toggles `completed` boolean field), delete tasks; each task is scoped to `request.user`

<img width="1920" height="1080" alt="Screenshot 2026-04-15 195930" src="https://github.com/user-attachments/assets/38dbffda-9761-4fa2-9859-16e3da75fef0" />





---

# Tech Stack

| Layer        | Technology                                      |
|--------------|-------------------------------------------------|
| Backend      | Django 4.x (Python 3.12)                        |
| Auth         | Django session auth + optional Firebase (GitHub)|
| Database     | SQLite (dev) / PostgreSQL via `DATABASE_URL` (prod) |
| Text    | Integrated via frontend editor in dashboard     |
| Deployment   | Railway (Gunicorn + Procfile)                   |
| Environment  | `python-dotenv` for `.env` loading              |

---
# Architecture

```
              browser
      templates + js + firebase sdk
         |                 |
   http, session,     github popup
   csrf cookie             |
         |                 |
         v                 v
+--------------------+   +-------------+
| gunicorn           |   | firebase    |
|                    |   | auth        |
|  whitenoise        |   | (github)    |
|    /static/        |   +------+------+
|                    |          ^
|  django 5.2        |          |
|    middleware      |          | verify_id_token
|    todoapp.urls    |          |
|      /accounts ---------------+
|      /todos        |
|      /admin        |
|    orm             |
+---------+----------+
          |
          v
  postgres (sqlite if no DB_* vars)
```

# Session table:

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

# Database — SQLite (Default) & PostgreSQL

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

## PostgreSQL (Production — Railway)

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

# Project Structure

```
/                          redirects to /todos/
/todos/                    dashboard
/todos/add/                POST
/todos/toggle/<id>/
/todos/delete/<id>/
/todos/notes/save/         POST, JSON
/todos/notes/get/<id>/     JSON
/todos/notes/delete/<id>/  JSON
/accounts/login/
/accounts/register/
/accounts/logout/
/accounts/firebase/session/  POST, JSON
/admin/
```


---

# Environment Variables

Copy `.env.example` to `.env` in the project root. Django loads it on startup via `python-dotenv`.

```env
# Core Django

DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

CSRF_TRUSTED_ORIGINS= 
# Railway provides DATABASE_URL automatically when PostgreSQL is attached

# Firebase Auth (GitHub) — from Firebase console → Project settings → Your apps (Web) + Service accounts
FIREBASE_WEB_API_KEY=
FIREBASE_AUTH_DOMAIN=
FIREBASE_PROJECT_ID=
FIREBASE_APP_ID=
FIREBASE_MESSAGING_SENDER_ID=
# Server: path to service account JSON file (local), OR set FIREBASE_SERVICE_ACCOUNT_JSON to the raw JSON (Railway)
# GOOGLE_APPLICATION_CREDENTIALS=/path/to/serviceAccount.json
# FIREBASE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}


DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432

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

```bash
python manage.py makemigrations todos
python manage.py migrate
```

Run this whenever you:
- Set up a new local environment
- Pull changes that include new model fields
- Deploy to a new server


