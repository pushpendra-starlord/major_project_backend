from django.db.models.manager import EmptyManager
from django.shortcuts import render
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from .models import Story
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
            print(stories)
            user_list = Story.objects.filter(pk__in = stories).values_list("user", flat=True).order_by("-id")        
            user_list = User.objects.filter(pk__in = list(user_list))
            serializer = UserSerializer(user_list, many = True)
            output_data = serializer.data
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


        

        



