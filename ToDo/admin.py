from django.contrib import admin
from .models import ToDo, SubTask, Notes, TaskList, Attachments

admin.site.register(ToDo)
admin.site.register(SubTask)
admin.site.register(Notes)
admin.site.register(TaskList)
admin.site.register(Attachments)