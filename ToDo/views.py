from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ToDo
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from users.models import Profile
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin


def home(request):
    context = {
        "todos": ToDo.objects.all()
    }
    return render(request, "ToDo/home.html", context)


def delete(request, pk):
    todo = ToDo.objects.get(pk=pk)

    if not todo.is_checked:
        user = User.objects.get(username=request.user.username)
        user.profile.todos -= 1
        user.save()

    todo.delete()
    messages.info(request, "item removed !!") 

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


class TodoListView(ListView):
    model = ToDo
    template_name = "ToDo/home.html"
    context_object_name = "todos"
    ordering = ["-date_posted"]


class TodoCompletedView(ListView):
    model = ToDo
    template_name = "ToDo/completed.html"
    context_object_name = "todos"
    ordering = ["-date_posted"]


class TodoCreateView(LoginRequiredMixin, CreateView):
    model = ToDo
    fields = ["title"]
    success_url = reverse_lazy("todo-home")
    
    def form_valid(self, form):
        form.instance.creator = self.request.user
        user = User.objects.get(username=self.request.user.username)
        user.profile.todos += 1
        user.save()
        messages.success(self.request, "Your new task has been added")
        return super().form_valid(form)


class TodoUpdateView(LoginRequiredMixin, UpdateView):
    model = ToDo
    fields = ["title"]
    success_url = reverse_lazy("todo-home")

    def form_valid(self, form):
        form.instance.creator = self.request.user
        messages.info(self.request, "Your task has been edited")
        return super().form_valid(form)