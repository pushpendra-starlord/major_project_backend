from django.shortcuts import render
from rest_framework.serializers import ListSerializer
from rest_framework.settings import APISettings, import_from_string
from blog.serializer import *
from blog.models import *
from shared.views import CreateUpdateDeleteView
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

# Create your views here.
           
class BlogPostView(CreateUpdateDeleteView):
    model=BlogPost
    serializer=BlogPostSerializer

class LikeView(CreateUpdateDeleteView):
    model=Like
    serializer=ListSerializer

class CommentView(CreateUpdateDeleteView):
    model=Comment
    serializer=CommentSerializer

class ListBlogView(APIView):
    def get(self, request, *args, **kwargs):
        user=request.user
        output_status=False
        output_detail="Falied"
        res_status=status.HTTP_400_BAD_REQUEST
        data={}
        model=BlogPost.objects.all()
        if model:
            serializer=BlogPostSerializer(model,many=True)
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


