from datetime import datetime
from django.db import models
from django.utils import timezone
from authentication.models import User

# Create your models here.

class Story(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to= "stories")
    expired = models.BooleanField(default= False)
    created_at = models.DateTimeField(timezone.now())


class Viewer(models.Model):
    story = models.OneToOneField(Story, on_delete=models.CASCADE)
    viewers = models.ManyToManyField(User, blank=True)


class StoryStream(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    following_user = models.ForeignKey(User , on_delete= models.CASCADE, related_name="following_user")
    viewed_story = models.ManyToManyField(Story, related_name="viewed_story", blank=True )
    
