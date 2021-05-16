from django.urls import path,include
from .views import FollowList, BlockListApiView, UnfollowView, UnblockView

urlpatterns =[
    path('followlist/', FollowList.as_view()),
    path('unfollow/', UnfollowView.as_view()),
    path('blocklist/', BlockListApiView.as_view()),
    path('unblock/', UnblockView.as_view()),

]