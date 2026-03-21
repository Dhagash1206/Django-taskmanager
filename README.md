# TaskMate — Django Todo + Notes App

A full-featured Django app with user auth, todo tasks, and rich text notes.

## Features
- ✅ Protected dashboard (login required)
- ✅ User registration & login
  <img width="844" height="777" alt="Screenshot 2026-03-18 111259" src="https://github.com/user-attachments/assets/8455deab-3ce5-446f-9e39-aa9ba86d2438" />
- ✅ Todo list — add, complete, delete tasks
  <img width="946" height="474" alt="Screenshot 2026-03-18 111433" src="https://github.com/user-attachments/assets/7d297077-9eb6-4241-bf4a-de46d3834cd0" />
- ✅ Notes — create, auto-save, delete rich text notes
  <img width="956" height="456" alt="Screenshot 2026-03-18 111731" src="https://github.com/user-attachments/assets/f6c7cf14-859a-4c74-8f75-148665bfa8b8" />
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
├── todoapp/           
│   ├── settings.py
│   └── urls.py
├── accounts/          
│   ├── views.py
│   └── urls.py
├── todos/            
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

---

## Deploy on Railway

1. Push the repo to GitHub.
2. Create a new project in Railway and connect this repo.
3. Add a PostgreSQL service in Railway (this sets `DATABASE_URL` automatically).
4. Add these Railway environment variables:
   - `SECRET_KEY` = strong random value
   - `DEBUG` = `False`
   - `ALLOWED_HOSTS` = your Railway domain (comma-separated if multiple)
   - `CSRF_TRUSTED_ORIGINS` = `https://<your-domain>`
5. Deploy. The `Procfile` runs migrations, collects static files, and starts Gunicorn.
