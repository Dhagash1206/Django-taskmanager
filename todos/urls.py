from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add/', views.add_todo, name='add_todo'),
    path('toggle/<int:pk>/', views.toggle_todo, name='toggle_todo'),
    path('delete/<int:pk>/', views.delete_todo, name='delete_todo'),
    path('notes/save/', views.save_note, name='save_note'),
    path('notes/delete/<int:pk>/', views.delete_note, name='delete_note'),
    path('notes/get/<int:pk>/', views.get_note, name='get_note'),
]
