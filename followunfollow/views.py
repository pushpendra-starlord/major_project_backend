from authentication.models import User
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Follow, BlockList 
from .serializers import FollowSerializer, BlockSerializer
from rest_framework.exceptions import MethodNotAllowed
from .utils import unfollow_block, unblock, unfollow
from notification.models import NotificationModel

# Create your views here.


# Follow View


class FollowBLockApiView(APIView):
    MODELCLASS = None
    SERIALIZER_CLASS = None


    def get_queryset(self, request, *args, **kwargs):
        user = request.user
        return self.MODELCLASS.objects.filter(user= user.id).first()

    def get(self, request, *args, **kwargs):
        output_status = False
        output_detail = "Failed"
        res_status = status.HTTP_400_BAD_REQUEST
        output_data = {}
        id = request.GET.get("id")
        if id:
            obj = self.MODELCLASS.objects.filter(user_id = id).first()
        else:
            obj = self.get_queryset(request)
        if obj:
            serializer = self.SERIALIZER_CLASS(obj)
            output_data = serializer.data
            output_status = True
            output_detail = "Success"
            res_status = status.HTTP_200_OK

        
        context = {
            "status" : output_status,
            "detail" : output_detail,
            "data" : output_data
        }
        return Response(context, status = res_status)

    def check_is_self(self,request,id):
        user = request.user 
        if user.id == id:
            return True
        else:
            return False

    def get_restrict(self,user,id):
        restrict_list = BlockList.objects.filter(user = user).values_list('restricted', flat = True)
        if id in restrict_list:
            return True
        else:
            return False

    def get_blocked(self,user,id):
        block_list = BlockList.objects.filter(user = user).values_list('blocked', flat = True)
        if id in block_list:
            return True
        else:
            return False

    def followed(self,user,id):
        followlist = Follow.objects.filter(user = user).values_list('following', flat = True)
        if id in followlist:
            return True
        else:
            return False





class FollowList(FollowBLockApiView):
    MODELCLASS = Follow
    SERIALIZER_CLASS = FollowSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        output_status = False
        output_detail = "Failed"
        res_status = status.HTTP_400_BAD_REQUEST
        id = int(request.data.get('id'))
        is_self = self.check_is_self(request,id)
    
        if is_self == True:
            output_detail = "is self"
            
        else:
            block_check = self.get_blocked(user, id)
            if block_check == True:
                output_detail = "You have Blocked the User"
            else:
                restrict_check = self.get_restrict(user, id)
                if restrict_check == True:
                    output_detail = "You are Blocked by the user"
                else:
                    follow_check = self.followed(user,id)
                    if follow_check == True:
                        output_detail = "You already Followed the User"
                    else:
                        obj = self.get_queryset(request)
                        z = User.objects.get(pk = int(id))
                     
                        obj.following.add(z)
                        other_list = self.MODELCLASS.objects.get(user = z)
                        other_list.follower.add(user)
                        
                        NotificationModel.objects.create(
                            user_id = id,
                            type = 1,
                            notifier = user,
                            comment = f'{user.first_name} {user.last_name} started following you.'
                        )
                        output_status = True
                        output_detail = "Success"
                        res_status = status.HTTP_200_OK
        context = {
            "status" : output_status,
            "detail" : output_detail,
        }
        return Response(context, status = res_status)



class BlockListApiView(FollowBLockApiView):
    MODELCLASS = BlockList
    SERIALIZER_CLASS = BlockSerializer


    def post(self, request, *args, **kwargs):
        user = request.user
        output_status = False
        output_detail = "Failed"
        res_status = status.HTTP_400_BAD_REQUEST
        id = int(request.data.get('id'))
        is_self = self.check_is_self(request,id)
        if is_self == True:
            output_detail = "is self"         
        else:
            block_check = self.get_blocked(user, id)
            if block_check == True:
                output_detail = "You Already Blocked the User"
            else:
                restrict_check = self.get_restrict(user, id)
                if restrict_check == True:
                    output_detail = "Unexpected Error"
                else:
                    unfollow_block(user,id)
                    blocker_list = self.get_queryset(request)
                    blocker_list.blocked.add(id)
                    restricted_list = self.MODELCLASS.objects.get(user__id = id)
                    restricted_list.restricted.add(user)
                    output_detail = "blocked"
                    output_status = True
        context = {
            "status" : output_status,
            "detail" : output_detail,
        }
        return Response(context, status = res_status)


class UnblockView(APIView):
    def post(self, request):
        user = request.user
        output_status = False
        output_detail = "Failed"
        res_status = status.HTTP_400_BAD_REQUEST
        id = int(request.data.get('id'))
        if id:
            check_user = User.objects.filter(pk = id).first()
            if check_user:
                unblock(user, id)
                output_status = True
                output_detail = "unblocked"
            else:
                output_detail = "invalid id"
        context = {
            "status" : output_status,
            "detail" : output_detail,
            }
        return Response(context, status = res_status)   

class UnfollowView(APIView):
    def post(self, request):
        user = request.user
        output_status = False
        output_detail = "Failed"
        res_status = status.HTTP_400_BAD_REQUEST
        id = int(request.data.get('id'))
        if id:
            check_user = User.objects.filter(pk = id).first()
            if check_user:
                unfollow(user, id)
                output_status = True
                output_detail = "unfollowed"
                res_status = status.HTTP_200_OK
            else:
                output_detail = "invalid id"
        context = {
            "status" : output_status,
            "detail" : output_detail,
            }
        return Response(context, status = res_status)   
     


                    
                    



            