from django.db.models import fields
from rest_framework import serializers
from shared.serializer import CustomModelSerializer
from blog.models  import *
from authentication.serializer import UserSerializer
from django.utils import timezone
import datetime



class CommentSerializer(CustomModelSerializer):
    user=UserSerializer(read_only=True)
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = "__all__"

    def get_created_at(self, obj):
        created = obj.created_at
        if created:
            difference = timezone.now() - created
            if difference.days > 0:
                return f"{difference.days} days ago"
            else:
                hour = int(difference.seconds//3600)
                if hour > 0:
                    return f"{hour} hours ago"
                elif int(difference.seconds//60) > 1 :
                    return f"{difference//60} minutes ago"
                else:
                    return "Just now"



class LikePostSerializer(CustomModelSerializer):
    user=UserSerializer(read_only=True)
    class Meta:
        model = Like
        fields = ("user",)

class BlogPostSerializer(serializers.ModelSerializer):
    comment= serializers.SerializerMethodField()
    like=serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    user = UserSerializer(read_only = True)
    created_at = serializers.SerializerMethodField()
    class Meta:
        model = BlogPost
        fields = "__all__"
    
    def get_comment(self,obj):
        blog_id = obj.id
        comment_data=Comment.objects.filter(post_id=blog_id)
        if comment_data:
            data=CommentSerializer(comment_data[:2],many=True).data
            data.append({
                "count":comment_data.count()-2 if comment_data.count() > 2 else ""
            })
            return data 
        return "" 

    def get_like(self,obj):
        blog_id = obj.id
        like_data=Like.objects.filter(post_id=blog_id)
        if like_data:
            data=LikePostSerializer(like_data[:1],many=True).data
            data.append({
                "count":like_data.count()-1 if like_data.count() > 1 else ""
            })
            return data 
        return "" 

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request:
            data = Like.objects.filter(post = obj , user = request.user).first()
            if data:
                return True
            else:
                return False
        return ""

    def get_owner(self,obj):
        request = self.context.get('request')
        if request:
            if obj.user == request.user:
                return True
            else:
                return False
        return ""

    def get_created_at(self, obj):
        created_at = obj.created_at
        difference = timezone.now() - created_at
        if difference.days > 0:
            return f"{difference.days} days ago"
        else:
            hour = difference.seconds//3600
            if hour > 0:
                return f"{hour} hours ago"
            elif difference.seconds//60 > 1 :
                return f"{difference//60} minutes ago"
            else:
                return "Just now"
            
        return ""

class CreateBlogSerializer(CustomModelSerializer):
    class Meta:
        model = BlogPost
        fields = "__all__"