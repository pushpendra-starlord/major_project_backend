from django.urls import path
from chat.views import PersonalChatView, ChatListView

urlpatterns = [
    path('<str:username>/', PersonalChatView.as_view()),
    path("get/chatlist/", ChatListView.as_view())
]