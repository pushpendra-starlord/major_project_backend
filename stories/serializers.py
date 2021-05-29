from django.db import models
from django.db.models import fields
from rest_framework import serializers
from . models import Story


class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = "__all__"