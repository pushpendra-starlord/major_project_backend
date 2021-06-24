from django.urls import path
from .consumer import ChatConsumer, GlobalChatConsumer

websocket_urlpatterns = [
   path('ws/chat/<str:username>/', ChatConsumer),
   path('ws/chat/global/<str:username>/', GlobalChatConsumer)
]