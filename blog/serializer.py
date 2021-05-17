from rest_framework import serializers
from shared.serializer import CustomModelSerializer
from blog.models  import *
from authentication.serializer import UserSerializer



class CommentSerializer(CustomModelSerializer):
    user=UserSerializer(read_only=True)
    class Meta:
        model = Comment
        fields = "__all__"

class LikePostSerializer(CustomModelSerializer):
    user=UserSerializer(read_only=True)
    class Meta:
        model = Like
        fields = "__all__"

class BlogPostSerializer(CustomModelSerializer):
    comment= serializers.SerializerMethodField()
    like=serializers.SerializerMethodField()
    class Meta:
        model = BlogPost
        fields = "__all__"
    
    def get_comment(self,obj):
        blog_id = obj.id
        comment_data=Comment.objects.filter(post_id=blog_id)
        if comment_data:
            data=CommentSerializer(comment_data[:2],many=True).data
            data.append({
                "count":comment_data.count()-2 if comment_data.count() > 2 else None
            })
            return data 
        return "" 

    def get_like(self,obj):
        blog_id = obj.id
        like_data=Like.objects.filter(post_id=blog_id)
        if like_data:
            data=LikePostSerializer(like_data[:1],many=True).data
            data.append({
                "count":like_data.count()-1 if like_data.count() > 1 else None
            })
            return data 
        return "" 