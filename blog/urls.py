from django.urls import path
from blog.views import BlogPostView,LikeView,CommentView

urlpatterns=[
    path("post/",BlogPostView.as_view()),
    path("like/",LikeView.as_view()),
    path("comment/",CommentView.as_view()),
]