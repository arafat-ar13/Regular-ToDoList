from django.urls import path

from . import views
from .views import (SubtaskUpdateView, TaskListUpdateView, TodoImportantView,
                    ToDoNextUpView, ToDoNotesUpdateView, TodoUpdateView)

urlpatterns = [
    path('', views.view_taskslists, name="todo-home"),
    path('todo/important/', TodoImportantView.as_view(), name="todo-important"),
    path('todo/next_up/', ToDoNextUpView.as_view(), name="todo-next-up"),
    path('todo/toggle_theme/', views.toggle_theme, name="toggle-theme"),
    path('todo/toggle_task/', views.toggle_todo, name="todo-toggle"),
    path('todo/toggle_important/', views.toggle_important_task, name="todo-toggle-important"),
    path('todo/toggle_subtask/', views.toggle_subtask, name="todo-toggle-subtask"),
    path('todo/edit_subtask/<int:pk>/',  SubtaskUpdateView.as_view(), name="todo-edit-subtask"),
    path('todo/edit_notes/<int:pk>/', ToDoNotesUpdateView.as_view(), name="todo-edit-notes"),
    path('todo/edit/<int:pk>/', TodoUpdateView.as_view(), name="todo-edit"),
    path('todo/<title>/<int:pk>/', views.todo_detail, name="todo-detailed"),
    path('tasklists/edit/<int:pk>/', TaskListUpdateView.as_view(), name="tasklist-edit"),
    path('tasklists/<title>/<int:pk>/', views.tasklist_single_view, name="tasklist-single-view"),
    path('tasklists/<title>/', views.tasklist_single_view, name="tasklist-single-view-default"),
    path('tasklists/', views.view_taskslists, name="view-tasklists"),
    path('search/', views.search, name="search"),
    path('create/', views.create, name="create"),
    path('delete/', views.delete, name='delete-item'),

]
