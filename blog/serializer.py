from rest_framework import serializers
from authentication.serializer import CustomModelSerializer
from blog.models  import *

class BlogPostSerializer(CustomModelSerializer):
    class Meta:
        model = BlogPost
        fields = "__all__"

class CommenttSerializer(CustomModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"

class LikePostSerializer(CustomModelSerializer):
    class Meta:
        model = Like
        fields = "__all__"