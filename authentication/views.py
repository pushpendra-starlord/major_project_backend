from authentication.utils import get_token
from rest_framework.views import APIView
from .models import User
from rest_framework import status
from rest_framework.response import Response



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
        if username_obj:
            if username_obj.check_password(password):
                data = get_token(username_obj)
            else:
                output_status = False
                res_status = status.HTTP_400_BAD_REQUEST
                detail = "Incorrect password"
        elif email_obj:
            if email_obj.check_password(password):
                data = get_token(username_obj)
            else:
                output_status = False
                res_status = status.HTTP_400_BAD_REQUEST
                detail = "Incorrect password"
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
            User.objects.create(username = username, password = password, email = email)
            output_detail = "Verify email"
                   



