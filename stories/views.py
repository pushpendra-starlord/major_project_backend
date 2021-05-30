from django.db import models
from django.db.models.manager import EmptyManager
from django.shortcuts import render
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from .models import Story, StoryStream, Viewer
from .serializers import StorySerializer, HomeStorySerializer
from followunfollow.models import Follow
from authentication.serializer import UserSerializer
from authentication.models import User

# Create your views here.

class StoryViewList(APIView):

    def get_following(self, user):
        story_obj = []
        following_list = Follow.objects.filter(user = user.id).values_list("following", flat=True)
        if following_list:
            for data in following_list:
                story_data =  Story.objects.filter(user = data).latest("id") 
                story_obj.append(story_data.id)
            return story_obj
        return None


    def get(self, request):
        output_status = False
        output_detail = "Failed"
        output_data = {}
        res_status = HTTP_400_BAD_REQUEST
        user = request.user
        stories = self.get_following(user)
        if stories:
            user_list = Story.objects.filter(pk__in = stories).values_list("user", flat=True).order_by("-id")        
            user_list = User.objects.filter(pk__in = list(user_list))
            serializer = HomeStorySerializer(user_list, many = True)
            pointer_dict = {}
            for i in user_list:
                story_data = StoryStream.objects.filter(user = user, following_user = i ).values_list("viewed_story", flat= True)
                pointer_dict[i.username] = list(story_data)

            output_data["pointers"] = pointer_dict
            output_data["story_data"] = serializer.data
            output_status = True
            output_detail = "Success"
            res_status = HTTP_200_OK
        else:
            output_detail = "No Story"
        
        context = {
            "status" : output_status,
            "detail" : output_detail,
            "data"  : output_data
        }
        return Response (context , status = res_status)

            

        
class StoryView(APIView):

    def get(self, request):
        output_status = False
        output_detail = "Failed"
        output_data = {}
        res_status = HTTP_400_BAD_REQUEST
        user = request.user
        story_id = request.GET.get("id")
        if story_id:
            story_obj = Story.objects.filter(pk = story_id).first()
            if story_obj:
                try:
                    stream_obj = StoryStream.objects.get(user = user, following_user = story_obj.user)
                except StoryStream.DoesNotExist:
                    stream_obj = StoryStream.objects.create(user = user, following_user = story_obj.user)
                stream_obj.viewed_story.add(story_id)

                try:
                    viewer_obj = Viewer.objects.get(story = story_obj)
                except Viewer.DoesNotExist:
                    viewer_obj = Viewer.objects.create(story = story_obj)
                viewer_obj.viewers.add(user)

                serializer = StorySerializer(story_obj)
                output_status = True
                output_detail = "Success"
                output_data = serializer.data
                res_status = HTTP_200_OK
            else:
                output_detail = "Invalid Id"
        else:
            story_obj = Story.objects.filter(user = user)
            if story_obj:
                serializer = StorySerializer(story_obj)
                output_status = True
                output_detail = "Success"
                output_data = serializer.data
                res_status = HTTP_400_BAD_REQUEST
            else:
                output_detail = "No story present"
        context = {
            "status" : output_status,
            "detail" : output_detail,
            "data"  : output_data
        }
        return Response (context , status = res_status)
        
        
    def post(self, request):
        output_status = False
        output_detail = "Failed"
        output_data = {}
        res_status = HTTP_400_BAD_REQUEST
        user = request.user
        extra_data = {
            "user":user.id
        }
        serializer = StorySerializer(request.data, extra_data = extra_data)
        if serializer.is_valid():
            serializer.save()
            output_detail = "Success"
            output_status = True
            res_status = HTTP_200_OK
        else:
            output_data = serializer.errors
        
        context = {
            "status" : output_status,
            "detail" : output_detail,
            "data"  : output_data
        }
        return Response (context , status = res_status)

        




