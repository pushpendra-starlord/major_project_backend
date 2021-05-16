from django.shortcuts import render
from rest_framework.serializers import ListSerializer
from rest_framework.settings import import_from_string
from blog.serializer import *
from blog.models import *
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

# Create your views here.
class CreatelistView(APIView):
    model=None
    serializer=None
    def post(self, request, *args, **kwargs):
        user=request.user
        output_status=False
        output_detail="Falied"
        res_status=status.HTTP_400_BAD_REQUEST
        data={}
        extra_data={
            "user":user.id
        }
        serializer=self.serializer(data=request.data,extra_data=extra_data)
        if serializer.is_valid():
            serializer.save()
            output_status=True
            output_detail="Success"
            res_status=status.HTTP_200_OK
            data=serializer.data
        else:
            output_detail=serializer.errors
        context={
            "status":output_status,
            "detail":output_detail,
            "data":data
        }
        return Response(context, status=res_status)



class BlogPostView(CreatelistView):
    model=BlogPost
    serializer=BlogPostSerializer

class LikeView(CreatelistView):
    model=Like
    serializer=ListSerializer

class CommentView(CreatelistView):
    model=Comment
    serializer=CommenttSerializer


