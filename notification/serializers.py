from django.db import models
from rest_framework import serializers
from .models import NotificationModel


class NotificationModelSerializer(serializers.ModelSerializer):
    notifier = serializers.SerializerMethodField()
    post_data = serializers.SerializerMethodField()

    class Meta:
        model = NotificationModel
        fields = ("type", "comment", "notifier", "post", "post_data")

    def get_notifier(self, obj):
        notifier_user = obj.notifier
        if notifier_user:
            if obj.type == 1:
                return {
                    "username" : notifier_user.username,
                    "pic" : notifier_user.profile_image.url,
                    "id" : notifier_user.id
                }
            else:
                return notifier_user.username
        return ""

    def get_post_data(self, obj):
        post_data = obj.post
        if post_data:
            return post_data.image.url
        else:
            return ""

    