from django.urls import path
from . import views
from .views import (
    TodoCompletedView,
    TodoUpdateView,
    SubtaskUpdateView,
    ToDoNotesUpdateView
)

urlpatterns = [
    path('', views.home, name="todo-home"),
    path('todo/completed/', TodoCompletedView.as_view(), name="todo-completed"),
    path('todo/darkmode/', views.toggle_dark_mode, name="todo-darkmode"),
    path('todo/toggle_sort/', views.toggle_user_sort, name="todo-user-sort"),
    path('todo/delete_task/<int:pk>', views.delete, name="todo-delete-task"),
    path('todo/remove_due/<title>', views.remove_due_date, name="todo-due-remove"),
    path('todo/check/<title>', views.check_todo, name="todo-check"),
    path('todo/uncheck/<title>', views.uncheck_todo, name="todo-uncheck"),
    path('todo/<title>', views.todo_detail, name="todo-detailed"),
    path('todo/edit/<int:pk>', TodoUpdateView.as_view(), name="todo-edit"),
    path('todo/edit_subtask/<int:pk>',  SubtaskUpdateView.as_view(), name="todo-edit-subtask"),
    path('todo/delete_subtask/<title>', views.delete_subtask, name="todo-delete-subtask"),
    path('todo/toggle_subtask/<title>', views.toggle_subtask, name="todo-toggle-subtask"),
    path('todo/delete_notes/<content>', views.delete_notes, name="todo-delete-notes"),
    path('todo/edit_notes/<int:pk>', ToDoNotesUpdateView.as_view(), name="todo-edit-notes"),
    path('todo/toggle_important/<title>', views.toggle_important_task, name="todo-toggle-important"),
    path('todo/filter_todos/<filter_type>', views.filter_todos, name="todo-filter"),
    path('tasklists', views.view_taskslists, name="view-tasklists")
]
