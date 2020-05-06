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
    path('todo/remove_due/<int:pk>', views.remove_due_date, name="todo-due-remove"),
    path('todo/check/<int:pk>', views.check_todo, name="todo-check"),
    path('todo/uncheck/<int:pk>', views.uncheck_todo, name="todo-uncheck"),
    path('todo/filter_todos/<filter_type>', views.filter_todos, name="todo-filter"),
    path('todo/toggle_important/<int:pk>', views.toggle_important_task, name="todo-toggle-important"),
    path('todo/toggle_subtask/<int:pk>', views.toggle_subtask, name="todo-toggle-subtask"),
    path('todo/edit_subtask/<int:pk>',  SubtaskUpdateView.as_view(), name="todo-edit-subtask"),
    path('todo/edit_notes/<int:pk>', ToDoNotesUpdateView.as_view(), name="todo-edit-notes"),
    path('todo/edit/<int:pk>', TodoUpdateView.as_view(), name="todo-edit"),
    path('todo/<title>/<int:pk>', views.todo_detail, name="todo-detailed"),
    path('delete/<item_type>/<int:pk>', views.delete, name='delete-item'),
    path('tasklists', views.view_taskslists, name="view-tasklists"),
    path('tasklists/<title>/<int:pk>', views.tasklist_single_view, name="tasklist-single-view")
]
