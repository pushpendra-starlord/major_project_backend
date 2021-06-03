from rest_framework import serializers
import rest_framework
from rest_framework import status
from rest_framework.serializers import Serializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from authentication.models import User
from authentication.serializer import UserSerializer
from followunfollow.models import BlockList



class SearchUserView(APIView):
    def get_block_list(self, user):
        restricted =list( BlockList.objects.filter(user = user).values_list("restricted" , flat=True))
        if restricted:
            return restricted
        else:
            return None



    def post(self, request):
        output_status = False
        output_detail = "Failed"
        output_data = {}
        res_status = HTTP_400_BAD_REQUEST
        data = request.data.get("data")
        if data:
            data = data.split(" ")
            restricted = self.get_block_list(request.user)
            if restricted:
                all_user = User.objects.all().exclude(pk__in = restricted).exclude(pk = request.user.id)  
            else:
                all_user = User.objects.all().exclude(pk = request.user.id)  
            if len(data) >0:
                if len(data) == 1:
                    qs1 = all_user.filter(username__icontains = data[0])
                    qs2 = all_user.filter(first_name__icontains = data[0])
                    qs3 = all_user.filter(last_name__icontains = data[0])
                    
                else:
                    qs1 = all_user.filter(username__icontains = data[0])
                    qs2 = all_user.filter(first_name__icontains = data[0])
                    qs3 = all_user.filter(last_name__icontains = data[1])
                qs = qs1.union(qs2, qs3)
                serializer = UserSerializer(qs, many = True)
                output_detail = "Success"
                output_data = serializer.data
                output_status = True
                res_status = HTTP_200_OK
            else:
                output_detail = "Did not find a user corresponding to your serach"
        else:
            output_detail = "Please enter a value to be searched"
        context = {
            "status" : output_status,
            "detail" : output_detail,
            "data" : output_data
        }
        return Response(context, status = res_status)





