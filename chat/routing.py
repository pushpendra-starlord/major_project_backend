from django.urls import path
# from .consumer import ChatConsumer, GlobalChatConsumer
from .consumers import PersonalChatConsumer, GlobalChatConsumer

websocket_urlpatterns = [
   path('ws/chat/<str:username>/',PersonalChatConsumer),
   path('ws/chat/global/<str:username>/', GlobalChatConsumer),
  
]