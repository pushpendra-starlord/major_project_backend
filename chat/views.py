from chat.models import Thread
from rest_framework.views import APIView
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from authentication.models import User
from .serializers import ChatUserSerializer, MessageSerializer


class PersonalChatView(APIView):

    def get(self, request, *args, **kwargs):
        output_status = False
        output_detail = "Failed"
        res_status = HTTP_400_BAD_REQUEST
        output_data = {}
        user = request.user
        other_user = kwargs.get("username")
        other_user_obj = User.objects.filter(username = other_user).first()

        page = request.GET.get('page', '')
        try:
            page = int(page)
        except Exception as  e:
            page = 1

        if other_user_obj:
            user_serializer = ChatUserSerializer(other_user_obj)
            output_data["user_data"] = user_serializer.data
            thread_obj = Thread.objects.get_or_create_personal_thread(user, other_user_obj)
            msg_obj = thread_obj.message_set.all().order_by('-id')[20 * (page - 1):20 * page]
            if msg_obj:
                message_serializer = MessageSerializer(msg_obj, many = True)
                output_data["message"] = message_serializer.data
                output_data["last"] = False
            else:
                output_data["last"] = True
            
            output_status = True
            output_detail = "Success"
            res_status = HTTP_200_OK
        else:
            if page == 1:
                output_detail = "No conversation yet"
            else:
                output_detail = "invalid username"
        
        context = {
            "status" : output_status,
            "detail" : output_detail,
            "data" : output_data
        }
        return Response(context, status = res_status)

        


# class ChatList(APIView):
#     def get(self, request):
#         output_status = False
#         output_detail = "Failed"
#         res_status = HTTP_400_BAD_REQUEST
#         output_data = {}
#         user = request.user
#         chat_obj = Thread.objects.filter(users = user).order_by()
#         if chat_obj:

