from django.db import models
from blog.models import BlogPost, Comment
from authentication.models import User

# Create your models here.
class NotificationModel(models.Model):
    NOTIFICATION_TYPE = (
        (1, "FOLLOW"),
        (2, "LIKE"),
        (3, "COMMENT"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.PositiveSmallIntegerField(choices= NOTIFICATION_TYPE, default=1 )
    notifier = models.ForeignKey(User,on_delete=models.CASCADE, related_name= "notifier")
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, null= True, blank=True)
    comment = models.CharField(max_length= 500)

    def __str__(self):
        return f"{self.notifier.username} {self.comment}"