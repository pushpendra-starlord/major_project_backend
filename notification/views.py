import re
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from .models import NotificationModel
from .serializers import NotificationModelSerializer
# Create your views here.

class NotificationView(APIView):
    def get(self, request):
        output_status = False
        res_status = HTTP_400_BAD_REQUEST
        output_data = {}
        output_detail = "Unexpected Error"
        user = request.user
        notification_obj = NotificationModel.objects.filter(user = user)
        if notification_obj:
            serializer = NotificationModelSerializer(notification_obj, many = True)
            output_status = True
            output_detail = "successfull"
            output_data = serializer.data
            res_status = HTTP_200_OK
        else:
            output_detail = "No notification available"
            res_status = HTTP_200_OK
        
        context = {
            "status" : output_status,
            "detail" : output_detail,
            "data" : output_data
        }
        return Response(context, status = res_status )


def test_view(request):
    return render (request , "test.html")