from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class TaskList(models.Model):
    title = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    num_of_tasks = models.IntegerField(default=0)

    def __str__(self):
        return self.title + " List"


class ToDo(models.Model):
    title = models.CharField(max_length=100)
    parent_list = models.ForeignKey(
        TaskList, on_delete=models.CASCADE, null=True)
    date_created = models.DateTimeField(default=timezone.now)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    is_checked = models.BooleanField(default=False)
    due_date = models.DateTimeField(null=True, blank=True)
    due_date_color = models.CharField(max_length=100, null=True, blank=True)
    num_of_subtasks = models.IntegerField(default=0)
    date_completed = models.DateTimeField(null=True, blank=True)
    has_notes = models.BooleanField(default=False)
    important = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class SubTask(models.Model):
    title = models.CharField(max_length=100)
    done = models.BooleanField(default=False)
    parent_task = models.ForeignKey(ToDo, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Notes(models.Model):
    content = models.TextField(
        help_text="Add anything that's important to the task")
    date_added = models.DateField(auto_now_add=True)
    date_edited = models.DateField(auto_now=True)
    parent_task = models.ForeignKey(ToDo, on_delete=models.CASCADE)

    def __str__(self):
        return f"Notes of {self.parent_task.title}"
