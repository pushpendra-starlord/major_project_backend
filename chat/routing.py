from django.urls import path
from .consumer import ChatConsumer, GlobalChatConsumer, PersonalChatConsumer

websocket_urlpatterns = [
   path('ws/chat/<str:username>/',PersonalChatConsumer),
   path('ws/chat/global/<str:username>/', GlobalChatConsumer)
]