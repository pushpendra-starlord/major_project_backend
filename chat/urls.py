from django.urls import path
from chat.views import PersonalChatView

urlpatterns = [
    path('<str:username>/', PersonalChatView.as_view()),
]