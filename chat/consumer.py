from channels.consumer import AsyncConsumer
from asgiref.sync import sync_to_async
from django.db import models
from django.utils import timezone
from authentication.models import User
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Thread, Message, InScreenHistory
import json
from channels.db import database_sync_to_async
from django.utils import timezone
from blog.models import BlogPost


class ChatConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        me = self.scope['user']
        other_username = self.scope['url_route']['kwargs']['username']

        other_user = await sync_to_async(User.objects.get)(username=other_username)
        self.thread_obj = await sync_to_async(Thread.objects.get_or_create_personal_thread)(me, other_user)
        self.room_name = f'personal_thread_{self.thread_obj.id}'

        await self.channel_layer.group_add(self.room_name, self.channel_name)
        msg = json.dumps({
            self.scope['user'].username : True,
            other_username : await self.get_in_screen_status(other_user)
        })
        await self.send({
            'type': 'websocket.accept',
            
        })

        await self.update_in_screen_status(True)

        # msg = json.dumps({
        #     "username": self.scope['user'].username,
        #     "in_screen": True
        # })
        await self.channel_layer.group_send(self.room_name, {
            'type': 'websocket.message',
            "text": msg
        })

    async def websocket_receive(self, event):
        msg = json.dumps({
            'text': event.get('text'),
            'username': self.scope['user'].username,
            "time" : f"{timezone.now().hour}: {timezone.now().minute}"
        })
        await self.store_message(event.get('text'))

        await self.channel_layer.group_send(self.room_name,
                                            {
                                                'type': 'websocket.message',
                                                "text": msg
                                            }
                                            )

    async def websocket_message(self, event):
        await self.send({
            'type': 'websocket.send',
            "text": event["text"],
        }
        )

    async def websocket_disconnect(self, event):
        await self.update_in_screen_status(False)
        other_username = self.scope['url_route']['kwargs']['username']

        other_user = await sync_to_async(User.objects.get)(username=other_username)

        msg = json.dumps({
            self.scope['user'].username : await self.get_in_screen_status(self.scope['user']) ,
            other_username : await self.get_in_screen_status(other_user)
        })
        await self.channel_layer.group_send(self.room_name, {
            'type': 'websocket.message',
            "text": msg
        })
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    @database_sync_to_async
    def store_message(self, text):
        Message.objects.create(
            thread=self.thread_obj,
            sender=self.scope['user'],
            text=text,
            seen = True,
        )
        self.thread_obj.last_message = timezone.now()
        self.thread_obj.save()

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
    def get_in_screen_status(self, user_obj):
        try:
            obj = InScreenHistory.objects.get(
                thread_id=self.thread_obj.id, user_id = user_obj.id
            )
        except InScreenHistory.DoesNotExist:
            InScreenHistory.objects.create(thread_id=self.thread_obj.id, user_id = user_obj.id)
            obj = InScreenHistory.objects.get(
                thread_id=self.thread_obj.id, user_id = user_obj.id
            )
        return obj.in_screen

class GlobalChatConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        username = self.scope['url_route']['kwargs']['username']
        self.room_name = f'user_{username}'
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )

        await self.send({
            'type': 'websocket.accept'
        })

    async def websocket_disconnect(self, event):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def websocket_message(self, event):
        await self.send({
            'type': 'websocket.send',
            "text": event["text"],
        })
    async def websocket_receive(self, event):
        user = self.scope['user']
        username = self.scope['url_route']['kwargs']['username']
        
        other_user = await sync_to_async(User.objects.get)(username=username)
        self.thread_obj = await sync_to_async(Thread.objects.get_or_create_personal_thread)(user, other_user)

        msg = json.dumps({
                "id": self.thread_obj.id,
                "text": event.get("text"),
                'username': self.scope['user'].username,
                "time" : f"{timezone.now().hour}: {timezone.now().minute}"

            })
       
        await self.channel_layer.group_send(self.room_name, {
                'type': 'websocket.message',
                "text": msg
            })
        
        await self.store_message(event.get("text"))

    @database_sync_to_async
    def store_message(self, text):
        Message.objects.create(
            thread=self.thread_obj,
            sender=self.scope['user'],
            text=text
        )
        self.thread_obj.last_message = timezone.now()
        self.thread_obj.save()


class PersonalChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        me = self.scope['user']
        other_username = self.scope['url_route']['kwargs']['username']
        other_user = await sync_to_async(User.objects.get)(username=other_username)
        self.thread_obj = await sync_to_async(Thread.objects.get_or_create_personal_thread)(me, other_user)
        self.room_name = f'personal_thread_{self.thread_obj.id}'
        await self.channel_layer.group_add(self.room_name, self.channel_name)

        msg = json.dumps({
            self.scope['user'].username : True,
            other_username : await self.get_in_screen_status(other_user)
        })
        await self.update_in_screen_status(True)
        await self.accept()
        await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'websocket_message',
                    'message': msg
                }
        )
    

    # for disconnecting user
    async def disconnect(self, close_code):
        await self.update_in_screen_status(False)
        other_username = self.scope['url_route']['kwargs']['username']

        other_user = await sync_to_async(User.objects.get)(username=other_username)

        msg = json.dumps({
            self.scope['user'].username : await self.get_in_screen_status(self.scope['user']) ,
            other_username : await self.get_in_screen_status(other_user)
        })
        await self.channel_layer.group_send(self.room_name, {
            'type': 'websocket.message',
            "text": msg
        })
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )



    async def websocket_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
    

    async def receive(self, text_data):
        print(text_data)
        data = json.loads(text_data)
        if data['message']:
            msg = json.dumps({
                'username': self.scope['user'].username,
                "time" : f"{timezone.now().hour}: {timezone.now().minute}",
                "text": data['message']
            })
            await self.store_message(data,msg)
        else:
            model=BlogPost.objects.get(pk=data["post"])
            msg = json.dumps({
                'username': self.scope['user'].username,
                "time" : f"{timezone.now().hour}: {timezone.now().minute}",
                "text": model
            })



    @database_sync_to_async
    def store_message(self, text, post_id):
        if post_id:
            Message.objects.create(
                thread=self.thread_obj,
                sender=self.scope['user'],
                post_id = post_id,
                seen = True,
            )

        else:
            Message.objects.create(
                thread=self.thread_obj,
                sender=self.scope['user'],
                text=text,
                seen = True,
            )
        self.thread_obj.last_message = timezone.now()
        self.thread_obj.save()

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
    def get_in_screen_status(self, user_obj):
        try:
            obj = InScreenHistory.objects.get(
                thread_id=self.thread_obj.id, user_id = user_obj.id
            )
        except InScreenHistory.DoesNotExist:
            InScreenHistory.objects.create(thread_id=self.thread_obj.id, user_id = user_obj.id)
            obj = InScreenHistory.objects.get(
                thread_id=self.thread_obj.id, user_id = user_obj.id
            )
        return obj.in_screen

    