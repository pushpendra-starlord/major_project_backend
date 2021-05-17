from blog.serializer import BlogPostSerializer
from blog.models import BlogPost
from authentication.utils import get_token, otp_creation, get_following_count
from rest_framework.views import APIView
from .models import User
from rest_framework import status
from rest_framework.response import Response
from followunfollow.models import Follow, BlockList
from django.contrib.auth.validators import ASCIIUsernameValidator
from .serializer import UserProfileSerializer

validate_username = ASCIIUsernameValidator()


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


class ChangePassword(APIView):
    def post(self, request):
        output_status = False
        res_status = status.HTTP_400_BAD_REQUEST
        output_detail = "Unexpected Error"
        user = request.user
        old_password = request.data.get("old")
        new_password = request.data.get("new")
        confirm_password = request.data.get("confirm")
        if user.check_password(old_password) and new_password ==  confirm_password:
            user.set_password(new_password)
            output_detail = "Success"
            output_status = True
            res_status = status.HTTP_200_OK
        elif new_password == old_password:
            output_detail = "New Password cannot be same"
        elif new_password !=  confirm_password:
            output_detail = "Confirm Password must be same as new password"
        else:
            output_detail = "Your existing password is wrong"

        context = {
                "status": output_status,
                "details": output_detail,
            }
        return Response(context, status=res_status, content_type="application/json")


        

class UpdateUserName(APIView):
    # for checking the username availabilty
    def get(self, request):
        new_username = request.GET.get('username', '')
        res_status = status.HTTP_400_BAD_REQUEST
        context = {
            "status": False,
            "detail": 'Fail'
        }
        if len(new_username) < 6:
            new_username = None
        try:
            if new_username:
                validate_username(new_username)
        except Exception as e:
            new_username = None
        if not new_username:
            context['detail'] = 'Invalid Username'
            return Response(context, status=res_status)
        if User.objects.filter(username = new_username).exists():
            context["detail"]="Username Already exists"
        else:
            res_status = status.HTTP_200_OK
            context["status"]=True
            context["detail"]="Username is valid"
        return Response(context, status=res_status)


    def post(self, request):
        user = request.user
        new_username = request.data.get('username', '')
        res_status = status.HTTP_400_BAD_REQUEST
        context = {
            "status": False,
            "detail": 'Fail'
        }
        if new_username:
            if len(new_username) < 6 or user.username == new_username:
                new_username = None
            try:
                if new_username:
                    validate_username(new_username)
            except Exception as e:
                new_username = None
            if new_username:
                if User.objects.filter(username = new_username).exists():
                    context["detail"]="Username Already exists"
                else:
                    user.username = new_username
                    user.save()
                    res_status = status.HTTP_202_ACCEPTED
                    context["status"]=True
                    context["detail"]="Username updated successfully"
            else:
                context['detail'] = 'Invalid Username'
        return Response(context, status=res_status)


class ProfileView(APIView):
    def get(self, request):
        output_status = False
        res_status = status.HTTP_400_BAD_REQUEST
        output_detail = "Unexpected Error"
        output_data = {} 
        user = request.user
        username = request.GET.get('username')
        if username:
            user = User.objects.filter(username = username).first()
            if user:
                pass
            else:
                user = None
        else:
            user = request.user
        if user:
            output_data["user"] = UserProfileSerializer(user).data
            output_data["count"] = get_following_count(user)
            page = request.GET.get("page")
            try:
                page = int(page)
            except Exception as  e:
                page = 1
            blog_obj = BlogPost.objects.filter(user = user)[12 * (page - 1):12 * page] 
            output_data["blogs"] = BlogPostSerializer(blog_obj, many =True).data
            output_status = True
            output_detail = "Success"
            res_status = status.HTTP_200_OK
        
        context = {
            "status": output_status,
            "detail": output_detail,
            "data" : output_data
        }
        return Response(context, status=res_status)

    def post(self, requset):
        output_status = False
        output_detail = "Failed"
        output_data = {}
        user = requset.user
        serializer = UserProfileSerializer(user, data = requset.data, partial = True)
        if serializer.is_valid():
            serializer.save()
            output_status = True
            output_detail = "Success"
            res_status = status.HTTP_200_OK
            output_data = serializer.data
        else:
            output_data = serializer.errors

        context = {
            "status": output_status,
            "detail": output_detail,
            "data" : output_data
        }
        return Response(context, status=res_status)



            
                   



