from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ToDo
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from users.models import Profile
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import NewTaskForm, DueDateForm

import datetime


def home(request):
    if request.method == "POST":
        add_form = NewTaskForm(request.POST)

        if add_form.is_valid():
            title = add_form.cleaned_data.get("title")
            todo = ToDo(title=title)
            todo.creator = request.user
            todo.save()

            user = User.objects.get(username=request.user.username)
            user.profile.todos += 1
            user.save()
            messages.success(request, "Your new task has been added")

            return redirect("todo-home")

    else:
        add_form = NewTaskForm()

    context = {
        "todos": ToDo.objects.all().order_by("-date_posted"),
        "add_form": add_form
    }

    # Checking today's date and comparing colors of due dates
    today = datetime.datetime.today()
    todo_objects = ToDo.objects.all()

    for todo in todo_objects:
        if todo.due_date is not None:
            due_date = datetime.datetime.strptime(todo.due_date, ("%b %d"))
            if due_date.day > today.day:
                todo.due_date_color = "green"
            elif due_date.day == today.day:
                todo.due_date_color = "blue"
            elif due_date.day < today.day:
                todo.due_date_color = "red"

            todo.save()

    return render(request, "ToDo/home.html", context=context)


def add_due_date(request, pk):
    if request.method == "POST":
        due_form = DueDateForm(request.POST)
                
        if due_form.is_valid():
            days = due_form.cleaned_data.get("due_date")
            
            if days == "today":
                days = 0
            elif days == "tomorrow":
                days = 1
            else:
                days = int(days)

            today = datetime.datetime.today()
            due_date = today + datetime.timedelta(days=days)
            due_date = due_date.strftime("%b %d")

            todo = ToDo.objects.get(pk=pk)
            todo.due_date = due_date
            todo.save()

            messages.success(request, "Due Date added to task")

            return redirect("todo-home")
    else:
        due_form = DueDateForm

    context = {
        "due_form": due_form
    }

    return render(request, "ToDo/due_dates.html", context=context)
    

def remove_due_date(request, pk):
    todo = ToDo.objects.get(pk=pk)
    todo.due_date = None
    todo.due_date_color = None

    todo.save()
    messages.info(request, "Due Date removed")

    return redirect("todo-home")


def about(request):
    return render(request, "ToDo/about.html")


def delete(request, pk):
    todo = ToDo.objects.get(pk=pk)

    if not todo.is_checked:
        user = User.objects.get(username=request.user.username)
        user.profile.todos -= 1
        user.save()

    todo.delete()
    messages.info(request, "Item removed!!") 

    return redirect('todo-home') 

def check_todo(request, pk):
    todo = ToDo.objects.get(pk=pk)
    todo.is_checked = True
    todo.save()
    messages.success(request, "Sweeet! Congrats!!")

    user = User.objects.get(username=request.user.username)
    user.profile.todos -= 1
    user.save()

    return redirect("todo-home")

def uncheck_todo(request, pk):
    todo = ToDo.objects.get(pk=pk)
    todo.is_checked = False
    todo.save()

    user = User.objects.get(username=request.user.username)
    user.profile.todos += 1
    user.save()

    return redirect("todo-home")


class TodoCompletedView(ListView):
    model = ToDo
    template_name = "ToDo/completed.html"
    context_object_name = "todos"
    ordering = ["-date_posted"]


class TodoUpdateView(LoginRequiredMixin, UpdateView):
    model = ToDo
    fields = ["title"]
    success_url = reverse_lazy("todo-home")

    def form_valid(self, form):
        form.instance.creator = self.request.user
        messages.info(self.request, "Your task has been edited")
        return super().form_valid(form)