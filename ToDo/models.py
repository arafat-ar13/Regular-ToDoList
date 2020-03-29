from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class ToDo(models.Model):
    title = models.CharField(max_length=100)
    date_posted = models.DateTimeField(default=timezone.now)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    is_checked = models.BooleanField(default=False)
    due_date = models.DateTimeField(null=True, blank=True)
    due_date_color = models.CharField(max_length=100, null=True, blank=True)
    num_of_subtasks = models.IntegerField(default=0)
    date_completed = models.DateTimeField(null=True, blank=True)
    notes = models.BooleanField(default=False)
    important = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class SubTask(models.Model):
    title = models.CharField(max_length=100)
    done = models.BooleanField(default=False)
    # The attrs below will help in identifying which is the parent task of the particular sub task
    parent_task = models.CharField(max_length=150)
    identification_id = models.IntegerField(default="NOT_PROVIDED")

    def __str__(self):
        return self.title
        

class Notes(models.Model):
    content = models.TextField(help_text="Add anything that's important to the task")
    date_added = models.DateField(auto_now_add=True)
    date_edited = models.DateField(auto_now=True)
    # The attrs below will help in identifying which is the parent task of the particular sub task
    parent_task = models.CharField(max_length=150)
    identification_id = models.IntegerField(default="NOT_PROVIDED")

    def __str__(self):
        return f"Notes of {self.parent_task}"