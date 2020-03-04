from django.urls import path
from . import views
from .views import (
    TodoCompletedView,
    TodoUpdateView
)

urlpatterns = [
    path('', views.home, name="todo-home"),
    path('todo/completed/', TodoCompletedView.as_view(), name="todo-completed"),
    path('todo/delete/<int:pk>', views.delete, name="todo-delete"),
    path('todo/add_due/<int:pk>', views.add_due_date, name="todo-due"),
    path('todo/remove_due/<int:pk>', views.remove_due_date, name="todo-due-remove"),
    path('todo/check/<int:pk>', views.check_todo, name="todo-check"),
    path('todo/uncheck/<int:pk>', views.uncheck_todo, name="todo-uncheck"),
    path('todo/edit/<int:pk>', TodoUpdateView.as_view(), name="todo-edit"),
]
