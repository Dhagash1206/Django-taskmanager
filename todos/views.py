from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
import time
import uuid
from pathlib import Path
from .models import Todo, Note


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


@login_required
def dashboard(request):
    todos = Todo.objects.filter(user=request.user)
    notes = Note.objects.filter(user=request.user)
    _agent_log(
        "H1",
        "todos/views.py:dashboard",
        "Render dashboard",
        {"path": request.path, "todoCount": todos.count(), "noteCount": notes.count(), "uiVersion": "pro-dark-v2"},
    )
    return render(request, 'todos/dashboard.html', {'todos': todos, 'notes': notes})


@login_required
@require_POST
def add_todo(request):
    title = request.POST.get('title', '').strip()
    if title:
        Todo.objects.create(user=request.user, title=title)
    return redirect('/todos/')


@login_required
def toggle_todo(request, pk):
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    todo.completed = not todo.completed
    todo.save()
    return redirect('/todos/')


@login_required
def delete_todo(request, pk):
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    todo.delete()
    return redirect('/todos/')


@login_required
@require_POST
def save_note(request):
    data = json.loads(request.body)
    note_id = data.get('id')
    title = data.get('title', 'Untitled Note').strip() or 'Untitled Note'
    content = data.get('content', '')

    if note_id:
        note = get_object_or_404(Note, pk=note_id, user=request.user)
        note.title = title
        note.content = content
        note.save()
    else:
        note = Note.objects.create(user=request.user, title=title, content=content)

    return JsonResponse({'id': note.pk, 'title': note.title, 'updated_at': note.updated_at.strftime('%b %d, %Y')})


@login_required
def delete_note(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    note.delete()
    return JsonResponse({'ok': True})


@login_required
def get_note(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    return JsonResponse({'id': note.pk, 'title': note.title, 'content': note.content})
