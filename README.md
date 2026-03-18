# memo. — Django Todo + Notes App

A full-featured Django app with user auth, todo tasks, and rich text notes.

## Features
- ✅ User registration & login
- ✅ Protected dashboard (login required)
- ✅ Todo list — add, complete, delete tasks
- ✅ Notes — create, auto-save, delete rich text notes
- ✅ Dark theme UI with sidebar layout

---

## Quick Start

### 1. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run migrations
```bash
python manage.py migrate
```

## Fix: `OperationalError: no such table: todos_todo`

If you see this error when opening `/todos/`, it means the `todos` app migrations haven’t been created/applied yet (so the `Todo`/`Note` tables don’t exist).

Run:

```bash
python manage.py makemigrations todos
python manage.py migrate
```

### 4. (Optional) Create a superuser for Django admin
```bash
python manage.py createsuperuser
```

### 5. Start the server
```bash
python manage.py runserver
```

### 6. Open in browser
```
http://127.0.0.1:8000/
```

---

## Project Structure
```
todoapp/
├── manage.py
├── requirements.txt
├── todoapp/           ← Django project config
│   ├── settings.py
│   └── urls.py
├── accounts/          ← Login / Register / Logout
│   ├── views.py
│   └── urls.py
├── todos/             ← Todo tasks + Notes
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── templates/
│   ├── base.html
│   ├── accounts/
│   │   ├── login.html
│   │   └── register.html
│   └── todos/
│       └── dashboard.html
└── db.sqlite3         ← created after migrate
```

## URLs
| Path | Description |
|------|-------------|
| `/` | Redirects to dashboard |
| `/accounts/login/` | Login page |
| `/accounts/register/` | Register page |
| `/accounts/logout/` | Logout |
| `/todos/` | Main dashboard |
| `/admin/` | Django admin |
