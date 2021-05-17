import re
from django.db.models.deletion import RestrictedError
from django.shortcuts import render
from django.views.generic.base import View
from rest_framework import views
from rest_framework.settings import APISettings, import_from_string
from blog.serializer import *
from blog.models import *
from shared.views import CreateUpdateDeleteView
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from followunfollow.models import Follow , BlockList

# Create your views here.
           
class BlogPostView(CreateUpdateDeleteView):
    model=BlogPost
    serializer=BlogPostSerializer

class LikeView(CreateUpdateDeleteView):
    model=Like
    serializer=LikePostSerializer

class CommentView(CreateUpdateDeleteView):
    model=Comment
    serializer=CommentSerializer

class ListBlogView(APIView):

    def get_follower(self,user):
        following_list = list(Follow.objects.filter(user = user).values_list("following", flat = True))
        if following_list :
           return following_list
        else:
            return None

    def get_restricted_account(self, user):
        blocked = BlockList.objects.filter(user = user)  
        blocked_list = blocked.values_list("blocked",flat=True)
        Restricted_list=blocked.values_list("restricted",flat=True)
        if blocked_list   and Restricted_list  :
            return list(blocked_list) + list(Restricted_list)
        elif blocked_list:
            return list(blocked_list)
        elif Restricted_list:
            return list(Restricted_list)
        else:
            return None

    
    def get(self, request, *args, **kwargs):
        page = request.GET.get('page', '')
        try:
            page = int(page)
        except Exception as  e:
            page = 1
        user=request.user
        output_status=False
        output_detail="Falied"
        res_status=status.HTTP_400_BAD_REQUEST
        data={}
        Restricted_List=self.get_restricted_account(user)
        if Restricted_List:
            all_post = BlogPost.objects.exclude(user_id__in=Restricted_List)
        else:
            all_post=BlogPost.objects.all()
        public_post=all_post.filter(view_type=1)
        following_list=self.get_follower(user)
        private_post=all_post.filter(user_id__in=following_list,view_type=2)
        final=public_post[5 * (page - 1):5 * page] | private_post[5 * (page - 1):5 * page] 
        if final:
            serializer=BlogPostSerializer(final,many=True)
            output_status=True
            output_detail="Success"
            res_status=status.HTTP_200_OK
            data=serializer.data
        context={
            "status":output_status,
            "detail":output_detail,
            "data":data
        }
        return Response(context, status=res_status)


