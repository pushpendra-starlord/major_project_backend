from asgiref.sync import sync_to_async
from django.utils import timezone
from authentication.models import User
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Thread, Message, InScreenHistory
import json
from channels.db import database_sync_to_async
from django.utils import timezone
from blog.models import BlogPost
from rest_framework_simplejwt.tokens import RefreshToken



class GlobalChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        print(self.scope["user"].username)
        username = self.scope['url_route']['kwargs']['username']
        self.room_group_name = f'global_chat_{username}'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def websocket_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def recieve(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'websocket_message',
                'message': message
            }
        )
        

class PersonalChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        me = self.scope['user']
        other_username = self.scope['url_route']['kwargs']['username']
        self.other_user = await sync_to_async(User.objects.get)(username=other_username)
        self.thread_obj = await sync_to_async(Thread.objects.get_or_create_personal_thread)(me, self.other_user)
        self.room_group_name = f'personal_thread_{self.thread_obj.id}'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.update_in_screen_status(True)
        await self.accept()

    async def disconnect(self, close_code):
        await self.update_in_screen_status(False)
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def websocket_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))

    async def receive(self, text_data):
        json_data = json.loads(text_data)
        in_screen = await self.get_in_screen_status()
        other_username = self.scope['url_route']['kwargs']['username']
        message = json_data["content"]

        if json_data["type"] == "MESSAGE":
            await self.store_message(text=message, post_id=None)

            if in_screen == False:
                msg = {
                    "id": self.thread_obj.id,
                    'username': self.scope['user'].username,
                    "time": f"{timezone.now().hour}:{timezone.now().minute}",
                    "text": message
                }

                await self.channel_layer.group_send(
                    f"global_chat_{other_username}",
                    {
                        'type': 'websocket_message',
                        'message': msg
                    }
                )
            else:
                msg = {
                    'username': self.scope['user'].username,
                    "time": f"{timezone.now().hour}:{timezone.now().minute}",
                    "text": message,
                }
        else:
            await self.store_message(text=None, post_id=message)
            if in_screen == False:

                msg = {
                    "id": self.thread_obj.id,
                    'username': self.scope['user'].username,
                    "time": f"{timezone.now().hour}:{timezone.now().minute}",
                    "text": "sent a post"
                }

                await self.channel_layer.group_send(
                    f"global_chat_{other_username}",
                    {
                        'type': 'websocket_message',
                        'message': msg
                    }
                )

            else:
                blog_obj = sync_to_async(BlogPost.objects.get)(pk=id)

                msg = {
                    'username': self.scope['user'].username,
                    "time": f"{timezone.now().hour}:{timezone.now().minute}",
                    "data": {
                        "username": blog_obj.user.username,
                        "image": blog_obj.image,
                    },
                }
        await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'websocket_message',
                        'message': msg
                    }
                )

    @database_sync_to_async
    def update_in_screen_status(self, interupt):
        try:
            obj = InScreenHistory.objects.get(
                thread_id=self.thread_obj.id, user_id=self.scope['user'].id)
        except InScreenHistory.DoesNotExist:
            InScreenHistory.objects.create(
                thread_id=self.thread_obj.id, user_id=self.scope['user'].id)
            obj = InScreenHistory.objects.get(
                thread_id=self.thread_obj.id, user_id=self.scope['user'].id)
        obj.in_screen = interupt
        obj.save()

    @database_sync_to_async
    def get_in_screen_status(self):
        try:
            obj = InScreenHistory.objects.get(
                thread_id=self.thread_obj.id, user_id=self.other_user.id
            )
        except InScreenHistory.DoesNotExist:
            InScreenHistory.objects.create(
                thread_id=self.thread_obj.id, user_id=self.other_user.id)
            obj = InScreenHistory.objects.get(
                thread_id=self.thread_obj.id, user_id=self.other_user.id
            )
        return obj.in_screen

    @database_sync_to_async
    def store_message(self, text, post_id):
        if post_id:
            Message.objects.create(
                thread=self.thread_obj,
                sender=self.scope['user'],
                post_id=post_id,
                seen=True,
            )

        else:
            Message.objects.create(
                thread=self.thread_obj,
                sender=self.scope['user'],
                text=text,
                seen=True,
            )
        self.thread_obj.last_message = timezone.now()
        self.thread_obj.save()

   
