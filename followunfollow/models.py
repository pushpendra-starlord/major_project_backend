from django.db import models
from django.db.models import base
from authentication.models import User

# Create your models here.


class Follow(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    follower = models.ManyToManyField(User, related_name="follower", blank=True)
    following = models.ManyToManyField(User, related_name="following", blank=True)

    def __str__(self):
        return  self.user.username

class BlockList(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    blocked = models.ManyToManyField(User, related_name="blocked", blank=True)
    restricted = models.ManyToManyField(User, related_name="restricted", blank=True)