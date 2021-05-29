from django.urls import path
from .views import StoryViewList

urlpatterns = [
    path('storylist/', StoryViewList.as_view()),

]