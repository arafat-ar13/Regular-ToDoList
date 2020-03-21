from django.urls import path
from . import views
from .views import (
    TodoCompletedView,
    TodoUpdateView,
    SubtaskUpdateView
)

urlpatterns = [
    path('', views.home, name="todo-home"),
    path('todo/completed/', TodoCompletedView.as_view(), name="todo-completed"),
    path('todo/darkmode/', views.toggle_dark_mode, name="todo-darkmode"),
    path('todo/toggle-sort/', views.toggle_user_sort, name="todo-user-sort"),
    path('todo/delete/<int:pk>', views.delete, name="todo-delete"),
    path('todo/remove_due/<int:pk>', views.remove_due_date, name="todo-due-remove"),
    path('todo/check/<int:pk>', views.check_todo, name="todo-check"),
    path('todo/uncheck/<int:pk>', views.uncheck_todo, name="todo-uncheck"),
    path('todo/edit/<int:pk>', TodoUpdateView.as_view(), name="todo-edit"),
    path('todo/new_subtask/<int:pk>', views.add_subtask, name="todo-add-subtask"),
    path('todo/edit_subtask/<int:pk>', SubtaskUpdateView.as_view(), name="todo-edit-subtask"),
    path('todo/delete_subtask/<int:pk>', views.delete_subtask, name="todo-delete-subtask"),
    path('todo/toggle_subtask/<int:pk>', views.toggle_subtask, name="todo-toggle-subtask")
]
