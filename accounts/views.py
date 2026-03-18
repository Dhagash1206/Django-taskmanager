from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
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
    return render(request, 'accounts/login.html')


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
    return render(request, 'accounts/register.html')


def logout_view(request):
    logout(request)
    return redirect('/accounts/login/')
