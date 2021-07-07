import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import  sync_to_async
from channels.db import database_sync_to_async
from django.utils import timezone
from blog.models import BlogPost, Like, Comment
from followunfollow.models import Follow
from .models import NotificationModel
from asgiref.sync import  sync_to_async
from django.utils import timezone


class NotificationConsumer(AsyncWebsocketConsumer):

    # for connecting user
    async def connect(self):
        id = self.scope['url_route']['kwargs']['id']
        self.room_name = f'user_{id}'
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )
        if id == self.scope['user'].id:
            await self.update_status(True)
        

        await self.accept()

    # for disconnecting user
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )
        id = self.scope['url_route']['kwargs']['id']
        if id  == self.scope['user'].id:
            await self.update_status(False)

    
    

    async def receive(self, text_data):
        data = json.loads(text_data)
        user = self.scope['user']
        msg = {}
        user_id = self.scope['url_route']['kwargs']['id']
        
        
        if data["type"] == "LIKE":
            id = data["id"]
            post_data = await self.like_post(id)
            if post_data is not None:
                comment_message = f"{user.username} liked your post."
                msg = {
                    "post" : id,
                    "type" : 2 , 
                    "notifier": user.username,
                    "post_data": post_data,
                    "comment" : comment_message

                }
        elif data["type"] == "COMMENT":
            id = data["id"]
            content = data["content"]
            post_data = await self.comment_post(id,content)
            comment_message = f"{user.username} commented on your post."
            msg = {
                    "post" : id,
                    "type" : 3 , 
                    "notifier": user.username,
                    "post_data": post_data,
                    "comment" : comment_message

                }
        else:
            self.follow_user()
            comment_message = f"{user.username} started following you"
            notifier = {
                "username": user.username,
                "pic" : user.profile_image.url
            }
            msg = {
                "post" : "",
                "type" : 1,
                "notifier": notifier,
                "post_data" : "",
                "comment" : comment_message

            }
            
        if user_id != user.id:
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'websocket_message',
                    'message': msg
                }
            )
        
    async def websocket_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))


    # db operation for updating status
    @database_sync_to_async
    def update_status(self, online):
        user = self.scope['user']
        if online == True:
            user.is_online = True
        else:
            user.is_online = False
            user.last_login = timezone.now()
        user.save()

    @database_sync_to_async
    def like_post(self, id):
        user = self.scope["user"]
        try:
            Like.objects.create(post_id = id, user = user)
            post_data = BlogPost.objects.filter(pk = id).first()
            likes_count = Like.objects.filter(post_id = id).count()
            if likes_count >1:
                comment = f"{user.username} and {likes_count - 1} liked your post."
            notification_model = NotificationModel.objects.filter(user_id = self.scope['url_route']['kwargs']['id'],post_id = id, type = 2).first()
            if notification_model:
                notification_model.notifier = user
                notification_model.comment = comment
                notification_model.save()
            else:
                NotificationModel.objects.create(
                    user_id = self.scope['url_route']['kwargs']['id'],
                    post_id = id, 
                    type = 2,
                    notifier = user,
                    comment = f"{user.username} liked your post."
                )
            return post_data.image.url
        except Exception as e:
            return None

    @database_sync_to_async
    def comment_post(self, id, content):
        user = self.scope["user"]

        Comment.objects.create(post_id = id, user = user, content = content)

        post_data = BlogPost.objects.filter(pk = id).first()
        comments_count = Comment.objects.filter(post_id = id).count()
        if comments_count >1 :
            comment = f"{user.username} and {comments_count - 1} commented on your post."


        notification_model = NotificationModel.objects.filter(user_id = self.scope['url_route']['kwargs']['id'],post_id = id, type = 3).first()
        
        if notification_model:
            notification_model.notifier = user
            notification_model.comment = comment
            notification_model.save()
        else:
            NotificationModel.objects.create(
                    user_id = self.scope['url_route']['kwargs']['id'],
                    post_id = id, 
                    type = 2,
                    notifier = user,
                    comment = f"{user.username} commented on your post."
                )
        return post_data.image.url

    @database_sync_to_async
    def follow_user(self):
        id = self.scope['url_route']['kwargs']['id']
        user = self.scope["user"]
        folow_list = Follow.objects.filter(user_id = id).first()
        folow_list.follower.add(user)
        
        NotificationModel.objects.create(
            user_id = self.scope['url_route']['kwargs']['id'],
            type = 2,
            notifier = user,
            comment = f"{user.username} starrted following you"
        )