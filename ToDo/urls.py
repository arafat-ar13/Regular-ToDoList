from django.urls import path
from . import views
from .views import (
    TodoListView, 
    TodoCreateView, 
    TodoCompletedView,
    TodoUpdateView
)

urlpatterns = [
    path('', TodoListView.as_view(), name="todo-home"),
    path('todo/new/', TodoCreateView.as_view(), name="todo-create"),
    path('todo/completed/', TodoCompletedView.as_view(), name="todo-completed"),
    path('todo/delete/<int:pk>', views.delete, name="todo-delete"),
    path('todo/check/<int:pk>', views.check_todo, name="todo-check"),
    path('todo/uncheck/<int:pk>', views.uncheck_todo, name="todo-uncheck"),
    path('todo/edit/<int:pk>', TodoUpdateView.as_view(), name="todo-edit"),
]
