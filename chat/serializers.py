from django.db import models
from django.db.models import fields
from rest_framework import serializers
from authentication.models import User
from .models import Message, Thread



class ChatUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "is_online", "profile_image")


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(source='sender.username', read_only=True)
    class Meta:
        model = Message
        fields = ("sender", 'text', "timestamp",)


class ChatListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    last_message_data = serializers.SerializerMethodField()
    class Meta:
        model = Thread
        fields = ( "id","last_message", "user", "last_message_data",)

    def get_user(self, obj):
        users = obj.users.all()
        serializer = ChatUserSerializer(users, many = True)
        if serializer:
            return serializer.data
        return ""
    def get_last_message_data(self, obj):
        data = obj.message_set.last()
        if data:
            serializer = MessageSerializer(data)
            if serializer:
                return serializer.data
        else:
            return "No message yet"
        return ""   