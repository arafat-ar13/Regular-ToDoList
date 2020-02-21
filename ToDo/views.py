from django.shortcuts import render
from .models import ToDo


def home(request):
    context = {
        "todos": ToDo.objects.all()
    }
    return render(request, "ToDo/home.html", context)