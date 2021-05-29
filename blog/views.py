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

    def get(self, request):
        output_status = False
        output_detail = "Failed"
        res_status = status.HTTP_400_BAD_REQUEST
        output_data = {}
        id = request.GET.get("id")
        if id:
            post_obj = BlogPost.objects.filter(pk = id).first()
            serializer = BlogPostSerializer(post_obj)
            output_status = True
            output_data = serializer.data
            output_detail = "Success"
            res_status = status.HTTP_200_OK
        else:
            output_detail = "Invalid Id"
        
        context = {
            "status" : output_status,
            "detail" : output_detail,
            "data" : output_data
        }
        return Response (context, status = res_status)



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
        else:
            output_detail = "No content"
        context={
            "status":output_status,
            "detail":output_detail,
            "data":data
        }
        return Response(context, status=res_status)


class LikeView(APIView):
    def get(self, request, id):
        page = request.GET.get('page', '')
        try:
            page = int(page)
        except Exception as  e:
            page = 1
        output_status=False
        output_detail="Falied"
        res_status=status.HTTP_400_BAD_REQUEST
        output_data = {}
        post_obj = BlogPost.objects.filter(pk = id).first()
        if post_obj:
            likes = Like.objects.filter(post = post_obj)[20 * (page - 1):20 * page]
            if likes:
                serializer = LikePostSerializer(likes, many = True)
                output_detail = "Success"
                output_status = True
                res_status = status.HTTP_200_OK
                output_data = serializer.data
            else:
                output_detail = "Last"
        else:
            output_detail = "Invalid id"
        context={
            "status":output_status,
            "detail":output_detail,
            "data": output_data
        }
        return Response(context, status=res_status)
    

    def post(self, request, id):
        output_status=False
        output_detail="Falied"
        res_status=status.HTTP_400_BAD_REQUEST
        post_obj = BlogPost.objects.filter(pk = id).first()
        if post_obj:
            try:
                Like.objects.create(user = request.user, post = post_obj)
                output_status = True
                output_detail = "Liked"
                res_status = status.HTTP_200_OK
            except Exception as e:
                like_obj = Like.objects.filter(user = request.user, post = post_obj)
                like_obj.delete()
                output_status = True
                output_detail = "Unliked"
                res_status = status.HTTP_200_OK
        else:
            output_detail = "Invalid Post id"
        context={
            "status":output_status,
            "detail":output_detail,
        }
        return Response(context, status=res_status)



            




