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
    path('todo/delete/<title>', views.delete, name="todo-delete"),
    path('todo/remove_due/<title>', views.remove_due_date, name="todo-due-remove"),
    path('todo/check/<title>', views.check_todo, name="todo-check"),
    path('todo/uncheck/<title>', views.uncheck_todo, name="todo-uncheck"),
    path('todo/edit/<int:pk>', TodoUpdateView.as_view(), name="todo-edit"),
    path('todo/new_subtask/<title>', views.add_subtask, name="todo-add-subtask"),
    path('todo/edit_subtask/<int:pk>',  SubtaskUpdateView.as_view(), name="todo-edit-subtask"),
    path('todo/delete_subtask/<title>', views.delete_subtask, name="todo-delete-subtask"),
    path('todo/toggle_subtask/<title>', views.toggle_subtask, name="todo-toggle-subtask"),
    path('todo/add_notes/<title>', views.add_todo_note, name="todo-add-notes"),
    path('todo/delete_notes/<content>', views.delete_notes, name="todo-delete-notes"),
    path('todo/edit_notes/<int:pk>', ToDoNotesUpdateView.as_view(), name="todo-edit-notes"),
    path('todo/toggle_important/<title>', views.toggle_important_task, name="todo-toggle-important"),
    path('todo/filter_by_important', views.filter_by_important,name="todo-filter-important"),
    path('todo/filter_by_due_dates', views.filter_by_due_dates,name="todo-filter-due-dates"),
    path('todo/filter_normal', views.filter_normal, name="todo-filter-normal"),
]
