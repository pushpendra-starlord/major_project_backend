from channels.consumer import AsyncConsumer
from asgiref.sync import sync_to_async
from django.utils import timezone
from authentication.models import User

from .models import Thread, Message, InScreenHistory
import json
from channels.db import database_sync_to_async
from django.utils import timezone


class ChatConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        me = self.scope['user']
        other_username = self.scope['url_route']['kwargs']['username']

        other_user = await sync_to_async(User.objects.get)(username=other_username)
        self.thread_obj = await sync_to_async(Thread.objects.get_or_create_personal_thread)(me, other_user)
        self.room_name = f'personal_thread_{self.thread_obj.id}'

        await self.channel_layer.group_add(self.room_name, self.channel_name)
        
        await self.send({
            'type': 'websocket.accept'
        })
        await self.update_in_screen(True)
        msg = json.dumps({
            "user" : str(self.scope['user'].username),
            "online" : self.scope['user'].is_online,
            "in_screen" : True
        })
        await self.channel_layer.group_send(self.room_name, {
            'type': 'websocket.message',
            "text": msg
        })
    

    async def websocket_receive(self, event):
        msg = json.dumps({
            'text': event.get('text'),
            'username': self.scope['user'].username
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
        await self.update_user_status(False)
        msg = json.dumps({
            "user" : str(self.scope['user'].username),
            "online" : self.scope['user'].is_online,
            "in_screen" : False
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
            text=text
        )
        self.thread_obj.last_message = timezone.now()
        self.thread_obj.save()

    
    @database_sync_to_async
    def update_in_screen(self, in_screen):
        cnt = InScreenHistory.objects.filter(thread = self.thread_obj, user = self.scope['user']).first()
        if cnt == 0:
            cnt = InScreenHistory.objects.create(thread = self.thread_obj, user = self.scope['user']) 
            cnt = InScreenHistory.objects.filter(thread = self.thread_obj, user = self.scope['user']).first()  
        if in_screen == True:
            cnt.in_screen = True
            cnt.save()
        else:
            cnt.in_screen = False
            cnt.save()





    
    
