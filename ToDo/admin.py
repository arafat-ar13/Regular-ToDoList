from django.contrib import admin
from .models import ToDo, SubTask, Notes

admin.site.register(ToDo)
admin.site.register(SubTask)
admin.site.register(Notes)