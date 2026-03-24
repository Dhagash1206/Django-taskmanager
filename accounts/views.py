from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
import time
import uuid
from pathlib import Path


# region agent log
def _agent_log(hypothesis_id: str, location: str, message: str, data: dict):
    try:
        payload = {
            "sessionId": "38c11d",
            "runId": "ui-refresh",
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data,
            "timestamp": int(time.time() * 1000),
            "id": f"log_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}",
        }
        (Path(__file__).resolve().parent.parent / "debug-38c11d.log").open("a", encoding="utf-8").write(
            json.dumps(payload) + "\n"
        )
    except Exception:
        pass
# endregion


def _firebase_auth_context():
    if not (
        settings.FIREBASE_WEB_API_KEY
        and settings.FIREBASE_AUTH_DOMAIN
        and settings.FIREBASE_PROJECT_ID
    ):
        return {"firebase_web_enabled": False, "firebase_web_config": {}}
    cfg = {
        "apiKey": settings.FIREBASE_WEB_API_KEY,
        "authDomain": settings.FIREBASE_AUTH_DOMAIN,
        "projectId": settings.FIREBASE_PROJECT_ID,
    }
    if settings.FIREBASE_APP_ID:
        cfg["appId"] = settings.FIREBASE_APP_ID
    if settings.FIREBASE_MESSAGING_SENDER_ID:
        cfg["messagingSenderId"] = settings.FIREBASE_MESSAGING_SENDER_ID
    return {"firebase_web_enabled": True, "firebase_web_config": cfg}


def login_view(request):
    if request.user.is_authenticated:
        return redirect('/todos/')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('/todos/')
        messages.error(request, 'Invalid username or password.')
    _agent_log("H3", "accounts/views.py:login_view", "Render login", {"path": request.path, "method": request.method})
    ctx = _firebase_auth_context()
    ctx["firebase_github_prominent"] = True
    return render(request, "accounts/login.html", ctx)


def register_view(request):
    if request.user.is_authenticated:
        return redirect('/todos/')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        if password != password2:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
        elif len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            messages.success(request, f'Welcome, {username}!')
            return redirect('/todos/')
    _agent_log("H3", "accounts/views.py:register_view", "Render register", {"path": request.path, "method": request.method})
    return render(request, "accounts/register.html", _firebase_auth_context())


@require_POST
def firebase_session_view(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    id_token = payload.get("idToken") or payload.get("id_token")
    if not id_token:
        return JsonResponse({"error": "Missing idToken."}, status=400)

    from firebase_admin import auth as firebase_auth

    from .firebase_init import get_firebase_app

    app = get_firebase_app()
    if app is None:
        return JsonResponse(
            {"error": "Firebase is not configured on the server (service account missing)."},
            status=503,
        )

    try:
        decoded = firebase_auth.verify_id_token(id_token, app=app)
    except Exception:
        return JsonResponse({"error": "Invalid or expired token."}, status=401)

    prov = (decoded.get("firebase") or {}).get("sign_in_provider")
    if prov != "github.com":
        return JsonResponse({"error": "Only GitHub sign-in is allowed."}, status=400)

    uid = decoded.get("uid")
    if not uid:
        return JsonResponse({"error": "Invalid token payload."}, status=400)

    email = (decoded.get("email") or "").strip()
    base_username = f"gh_{uid}"[:150]

    user, created = User.objects.get_or_create(
        username=base_username,
        defaults={"email": email},
    )
    if created:
        user.set_unusable_password()
        user.save()
    elif email and user.email != email:
        user.email = email
        user.save(update_fields=["email"])

    login(request, user)
    return JsonResponse({"redirect": "/todos/"})


def logout_view(request):
    logout(request)
    return redirect('/accounts/login/')
