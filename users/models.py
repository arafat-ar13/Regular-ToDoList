from django.db import models
from django.contrib.auth.models import User
from PIL import Image

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default="default.jpg", upload_to="profile_pics")
    todos = models.IntegerField(default=0)
    has_dark_mode = models.BooleanField(default=False)
    sort_todos_by = models.CharField(max_length=100, default="date_added")
    total_todos = models.IntegerField(default=0)
    filter_todos_by = models.CharField(max_length=100, default="all_todos")
    num_of_important_tasks = models.IntegerField(default=0)
    # The attributes below are used by the Insights Page to analyze the user
    insights_enabled = models.BooleanField(default=False)
    last_insights_date = models.DateTimeField(null=True, blank=True)
    todos_created_this_week = models.IntegerField(default=0)
    todos_completed_this_week = models.IntegerField(default=0)
    todos_completed_on_time = models.IntegerField(default=0)
    generated_insights_this_week = models.BooleanField(default=False)
    efficiency_this_week = models.IntegerField(default=0)
    efficiency_change = models.IntegerField(default=0)
    efficiency_change_type = models.CharField(max_length=100, default="NOT_PROVIDED")

    def __str__(self):
        return f"{self.user.username} Profile"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)