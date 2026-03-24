# TaskMate — Django Todo + Notes App

A full-featured Django app with user auth, todo tasks, and rich text notes.

## Features
- ✅ Protected dashboard (login required)
- ✅ User registration & login (including optional **Sign in with GitHub** via Firebase)
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
│   │   ├── includes/
│   │   │   └── firebase_github.html
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
| `/accounts/firebase/session/` | POST: verifies Firebase ID token after GitHub popup (used by the app; not for browser navigation) |
| `/todos/` | Main dashboard |
| `/admin/` | Django admin |

---

## Precaution: Firebase Auth (GitHub)

GitHub sign-in uses **Firebase Authentication** in the browser and **Firebase Admin** on the server to verify ID tokens. If this is misconfigured, the “Continue with GitHub” flow will fail (popup errors, `401`/`503` from `/accounts/firebase/session/`, or no button at all).

**Before it works end to end:**

1. **Local environment variables:** copy `.env.example` to `.env` in the project root (`Django-taskmanager/.env`). Django loads `.env` on startup via `python-dotenv`. Until `FIREBASE_WEB_API_KEY`, `FIREBASE_AUTH_DOMAIN`, and `FIREBASE_PROJECT_ID` are set (in the shell or in `.env`), the login page will **not** show “Continue with GitHub”.
2. **Run migrations first.** If core tables (e.g. `auth_user`, sessions) are missing, login and registration can return **500** until you run `python manage.py migrate`. Do this on every new environment (local, Railway, etc.).
3. **Firebase Console — Authentication:** enable the **GitHub** provider and complete the GitHub OAuth application steps (client ID/secret configured inside Firebase).
4. **Authorized domains:** under Authentication → Settings, add **`localhost`** for local dev and your **production hostname** (e.g. your Railway URL). Missing domains often cause popup or redirect failures.
5. **Web SDK config (public):** set these environment variables so the login/register pages can load Firebase (see `.env.example`):
   - `FIREBASE_WEB_API_KEY`
   - `FIREBASE_AUTH_DOMAIN`
   - `FIREBASE_PROJECT_ID`
   - Optionally `FIREBASE_APP_ID` and `FIREBASE_MESSAGING_SENDER_ID` (match the values from Firebase → Project settings → Your apps → Web app).  
   **Note:** The “Continue with GitHub” button only appears when `FIREBASE_WEB_API_KEY`, `FIREBASE_AUTH_DOMAIN`, and `FIREBASE_PROJECT_ID` are all set.
6. **Service account (secret — server only):** the backend must verify tokens with a Firebase service account key:
   - **Local:** set `GOOGLE_APPLICATION_CREDENTIALS` to the path of the downloaded JSON key, **or**
   - **Railway / CI:** set `FIREBASE_SERVICE_ACCOUNT_JSON` to the **full JSON** content of that key (not the file path).  
   Without this, `POST /accounts/firebase/session/` returns **503** (“not configured on the server”).
7. **Never commit** the service account JSON or put it in the frontend. Only the **web** config belongs in public/env-as-config for the browser; the key is for Django only.

If you do not need GitHub login, you can leave the Firebase variables unset; username/password auth still works.

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
   - (Optional, for GitHub via Firebase) the `FIREBASE_*` web config values and `FIREBASE_SERVICE_ACCOUNT_JSON` as described in **Precaution: Firebase Auth (GitHub)** above.
5. Deploy. The `Procfile` runs migrations, collects static files, and starts Gunicorn.
6. If build fails on Python install, ensure Railway uses Python 3.12 (this repo pins it in `runtime.txt`).
