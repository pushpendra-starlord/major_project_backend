from django.utils import timezone
from blog.serializer import BlogPostSerializer
from blog.models import BlogPost
from authentication.utils import get_token, otp_creation, get_following_count
from rest_framework.views import APIView
from .models import User
from rest_framework import serializers, status
from rest_framework.response import Response
from followunfollow.models import Follow, BlockList
from django.contrib.auth.validators import ASCIIUsernameValidator
from .serializer import UserProfileSerializer
from django.conf import settings
from followunfollow.models import Follow , BlockList
validate_username = ASCIIUsernameValidator()


class LoginView(APIView):
    permission_classes = ()
    def post(self, request):
        output_status = True
        res_status = status.HTTP_200_OK
        detail = "Success"
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
                data = get_token(email_obj)
            else:
                output_status = False
                res_status = status.HTTP_400_BAD_REQUEST
                detail = "Incorrect password"

        elif username_obj.email_verified == False :
            output_status = False
            res_status = status.HTTP_302_FOUND
            detail = "Email Verificaction Pending"
            if email_obj:
                user = email_obj
            else:
                user = username_obj
            data = {
                "email" : user.email,
                "status": 1
            }
            if settings.DEBUG == True:
                user.otp_code = "123456"
                user.otp_created_at = timezone.now()
                user.save()
            else:
                otp_creation(user)
        elif email_obj.email_verified == False:
            output_status = False
            res_status = status.HTTP_302_FOUND
            detail = "Email Verificaction Pending"
            if email_obj:
                user = email_obj
            else:
                user = username_obj
            data = {
                "email" : user.email,
                "status": 1
            }
            if settings.DEBUG == True:
                user.otp_code = "123456"
                user.otp_created_at = timezone.now()
                user.save()
            else:
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
        email_obj = User.objects.filter(email= email).first()
        if obj:
            output_detail = "Username already exist"
            context = {
                "status": output_status,
                "details": output_detail,
                "data" : output_data,
            }
            return Response(context, status=res_status, content_type="application/json")
        
        elif email_obj:
            if email_obj.email_verified == True:
                output_detail = "user is registered with this email"
            else:
                if settings.DEBUG ==  True:
                    email_obj.otp_code = "123456"
                    email_obj.otp_created_at = timezone.now()
                    output_status = False
                    output_detail = "Email is registered but not verified, Please verify email"
                else:
                    otp_creation(email_obj)
                res_status = status.HTTP_200_OK
                output_data = {
                    "email" : email_obj.email,
                    "status" : 1
                }
        else:
            user_obj  = User.objects.create(username = username, email = email)
            user_obj.set_password(password)
            if settings.DEBUG == True:
                user_obj.otp_code = "123456"
                user_obj.otp_created_at = timezone.now()
                user_obj.save()
            else:
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
        
        following  = False
        
        id = int(request.GET.get('id')) if request.GET.get('id') else None
        if id:
            user = User.objects.filter(pk = id).first()
            if user:
                follow_obj = list(Follow.objects.filter(user = request.user).values_list("following", flat=True))
                block_obj = BlockList.objects.filter(user = request.user).values_list("blocked", flat = True)
                if id in follow_obj:
                    following = True
                elif id in list(block_obj):
                    output_status = True
                    output_detail = "Success"
                    res_status = status.HTTP_200_OK
                    output_data = {
                        "block" : True,
                        "user" : UserProfileSerializer(user).data,
                        "count" : get_following_count(user)
                    }
                    context = {
                        "status": output_status,
                        "detail": output_detail,
                        "data" : output_data
                    }
                    return Response(context, status=res_status)
                    
                output_data = {
                    "is_following" : following,
                }
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
            blog_obj = BlogPost.objects.filter(user = user)
            if blog_obj:
                serializer = BlogPostSerializer(blog_obj,context={'request': request}, many =True)
                output_data["blogs"] = serializer.data
            else:
                output_data["blogs"] = "None"
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


class EmailVerification(APIView):
    permission_classes = ()
    def post(self, request):
        output_status = False
        res_status = status.HTTP_400_BAD_REQUEST
        output_detail = "Unexpected Error"
        email = request.data.get("email", '')
        otp = request.data.get("otp", "")
        if email and otp:
            user_obj = User.objects.filter(email= email).first()
            time_difference = timezone.now() - user_obj.otp_created_at
            if user_obj.otp_code == otp and time_difference.seconds < 600:
                user_obj.email_verified = True
                user_obj.save()
                output_status = True
                output_detail = "otp verified"
                res_status = status.HTTP_200_OK

            else:
                output_detail = "invalid"
        else:
            output_detail = "Otp and Email are required field"
        context = {
            "status": output_status,
            "detail": output_detail,

        }
        return Response(context, status=res_status)




class PasswordReset(APIView):
    permission_classes = ()
    def get(self, request):
        output_status = False
        res_status = status.HTTP_400_BAD_REQUEST
        output_detail = "Unexpected Error"
        login_data = request.GET.get("login_data")
        user = None
        user_obj = User.objects.filter(username = login_data).first()
        if user_obj:
            user = user_obj
        else:
            user = User.objects.filter(email = login_data).first()
        if user:
            otp_creation(user)
            output_status = True
            output_detail = "Otp Sent"
            res_status = status.HTTP_200_OK
        else:
            output_detail = "invalid login detail"
        context = {
            "status": output_status,
            "detail": output_detail,

        }
        return Response(context, status=res_status)

    
    def post(self, request):
        output_status = False
        res_status = status.HTTP_400_BAD_REQUEST
        output_detail = "Unexpected Error"
        login_data = request.data.get("login_data")
        otp = request.data.get("otp")
        user = None
        user_obj = User.objects.filter(username = login_data).first()
        if user_obj:
            user = user_obj
        else:
            user = User.objects.filter(email = login_data).first()
        time_difference = timezone.now() - user_obj.otp_created_at
        if user and user.otp_code == otp and time_difference.seconds < 600:
            password = request.data.get("password")
            user.set_password(password)
            output_status = True
            output_detail = "Success"
            res_status = status.HTTP_200_OK
        context = {
            "status": output_status,
            "detail": output_detail,

        }
        return Response(context, status=res_status)
        




        

        




            
                   



