from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Create your models here.
class User(AbstractUser):
    GENDER = (
        (1, "MALE"),
        ( 2,"FEMALE")
    )
    dob = models.DateTimeField(null= True, blank= True)
    mobile = models.CharField(max_length=15, null= True, blank= True, unique= True)
    gender = models.SmallIntegerField(choices=GENDER, null= True, blank= True)
    blue_tick = models.BooleanField(default= False)
    otp_code = models.CharField(max_length=10, null=True, blank=True)
    otp_created_at = models.DateTimeField(default = timezone.now)
    email_verified = models.BooleanField(default=False)
    mobile_verified = models.BooleanField(default=False)
    profile_image = models.ImageField(upload_to='profile_image', default='profile_image/default_image.png')
