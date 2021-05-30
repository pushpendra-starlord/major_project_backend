from re import I
from django.db import models
from django.db.models import fields
from rest_framework import serializers
from . models import Story, Viewer, StoryStream
from authentication.models import User
from shared.serializer import CustomModelSerializer


class StorySerializer(CustomModelSerializer):
    class Meta:
        model = Story
        fields = "__all__"


class UserStorySerializer(serializers.ModelSerializer):
    views = serializers.SerializerMethodField()
    viewers = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = ("id", "views", "viewers", "file")

    def get_views(self, obj):
        story_id = obj.id
        if story_id:
            viewer_obj = "__all__"


class HomeStorySerializer(serializers.ModelSerializer):
    stories = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ("id","username", "profile_image", "stories", )
    
    def get_stories(self,obj):
        story_data =list( Story.objects.filter(user = obj, expired = False).values_list("id", flat=True)) 
        return story_data

    