import os

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.conf import settings


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
    has_attachments = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        if self.parent_list is not None:
            self.parent_list.num_of_tasks -= 1
            self.parent_list.save()

        super().delete(*args, **kwargs)


class SubTask(models.Model):
    title = models.CharField(max_length=100)
    done = models.BooleanField(default=False)
    parent_task = models.ForeignKey(ToDo, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        self.parent_task.num_of_subtasks -= 1
        self.parent_task.save()

        super().delete(*args, **kwargs)


class Notes(models.Model):
    content = models.TextField(
        help_text="Add anything that's important to the task")
    date_added = models.DateField(auto_now_add=True)
    date_edited = models.DateField(auto_now=True)
    parent_task = models.ForeignKey(ToDo, on_delete=models.CASCADE)

    def __str__(self):
        return f"Notes of {self.parent_task.title}"

    def delete(self, *args, **kwargs):
        self.parent_task.has_notes = False
        self.parent_task.save()

        print(f"Notes of {self.parent_task.title} was deleted")

        super().delete(*args, **kwargs)


def get_attachment_dir(instance, filename):
    return f"users/{instance.parent_task.creator.username}_{instance.parent_task.creator.pk}/task_attachments/{instance.parent_task.pk}/{filename}"


class Attachments(models.Model):
    content = models.FileField(null=True, blank=True, upload_to=get_attachment_dir, help_text="Add important documents or pictures")
    parent_task = models.ForeignKey(ToDo, on_delete=models.CASCADE)
    uploaded_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachments of {self.parent_task.title}"

    def delete(self, *args, **kwargs):
        self.parent_task.has_attachments = False
        self.parent_task.save()

        super().delete(*args, **kwargs)
