from django.db import models
from django.db.models import fields
from rest_framework import serializers
from authentication.models import User
from .models import Message



class ChatUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "is_active", "profile_image")


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(source='sender.username', read_only=True)
    class Meta:
        model = Message
        fields = ("sender", 'text', "timestamp",)