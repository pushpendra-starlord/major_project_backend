from django.db import models
from django.db.models import fields
from rest_framework import serializers
from .models import User
from rest_framework.fields import empty



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username', "first_name", "last_name", "profile_image")


