from authentication.utils import get_token, otp_creation
from rest_framework.views import APIView
from .models import User
from rest_framework import status
from rest_framework.response import Response
from followunfollow.models import Follow, BlockList


class LoginView(APIView):
    permission_classes = ()
    def post(self, request):
        output_status = True
        res_status = status.HTTP_400_BAD_REQUEST
        detail = "Unexpected error"
        data = {}
        login_data = request.data.get("login_data")
        password = request.data.get("password")
        username_obj = User.objects.filter(username = login_data ).first()
        email_obj = User.objects.filter(email = login_data ).first()
        if username_obj and username_obj.email_verified:
            if username_obj.check_password(password):
                data = get_token(username_obj)
            else:
                output_status = False
                res_status = status.HTTP_400_BAD_REQUEST
                detail = "Incorrect password"
        elif email_obj and email_obj.email_verified:
            if email_obj.check_password(password):
                data = get_token(username_obj)
            else:
                output_status = False
                res_status = status.HTTP_400_BAD_REQUEST
                detail = "Incorrect password"

        elif email_obj.email_verified or username_obj.email_verified:
            output_status = False
            res_status = status.HTTP_400_BAD_REQUEST
            detail = "Email Verificaction"
            if email_obj:
                user = email_obj
            else:
                user = username_obj
            data = {
                "email" : user.email,
                "status": 1
            }
            otp_creation(user)
        else:
            detail = "Entered data is not associated to any account"
            output_status = False
            res_status = status.HTTP_400_BAD_REQUEST
        context = {
            "status" : output_status,
            "detail" : detail,
            "data"   : data
        }
        return Response(context, status=res_status, content_type="application/json")



class RegisterView(APIView):
    permission_classes = ()

    def post(self, requset):
        output_status = False
        res_status = status.HTTP_400_BAD_REQUEST
        output_data = {}
        output_detail = "Unexpected Error"
        username = requset.data.get("username")
        password = requset.data.get("password")
        email = requset.data.get("email")
        
        obj = User.objects.filter(username = username)
        if obj:
            output_detail = "Username already exist"
            context = {
                "status": output_status,
                "details": output_detail,
                "data" : output_data,
            }
            return Response(context, status=res_status, content_type="application/json")

        else:
            user_obj  = User.objects.create(username = username, password = password, email = email)
            otp_creation(user_obj)
            Follow.objects.create(user = user_obj)
            block_list = BlockList.objects.create(user = user_obj)
            block_list.blocked.add(1)
            block_list.restricted.add(1)
            output_data["email"] = email
            output_data["status_code"] = 1
            output_status = True
            output_detail = "Success"
            res_status = status.HTTP_200_OK
            context = {
                "status": output_status,
                "details": output_detail,
                "data" : output_data,
            }
            return Response(context, status=res_status, content_type="application/json")



        
            


            
                   



