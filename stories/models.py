from datetime import datetime
from django.db import models
from django.utils import timezone
from authentication.models import User

# Create your models here.

class Story(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to= "stories")
    created_at = models.DateTimeField(timezone.now())


class Viewer(models.Model):
    story = models.OneToOneField(Story, on_delete=models.CASCADE)
    viewers = models.ManyToManyField(User, blank=True)
