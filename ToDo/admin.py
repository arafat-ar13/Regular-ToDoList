from django.contrib import admin
from .models import ToDo, SubTask

admin.site.register(ToDo)
admin.site.register(SubTask)