from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class ToDo(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
