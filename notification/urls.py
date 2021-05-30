from django.urls import path
from .views import NotificationView, test_view

urlpatterns = [
    path('', NotificationView.as_view()),
    path('test/', test_view),

]