from django.urls import path
from .views import StoryViewList, StoryView

urlpatterns = [
    path('storylist/', StoryViewList.as_view()),
    path('storyview/', StoryView.as_view()),

]