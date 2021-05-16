from django.db.models import fields
from rest_framework import serializers
from .models import Follow, BlockList
from authentication.serializer import UserSerializer



class FollowSerializer(serializers.ModelSerializer):
    follower = UserSerializer(read_only=True, many=True)
    following = UserSerializer(read_only=True, many=True)

    class Meta:
        model = Follow
        exclude = ('id', "user",)


class BlockSerializer(serializers.ModelSerializer):
    blocked = UserSerializer(read_only=True, many=True)
    class Meta:
        model = BlockList
        fields = ('blocked',)