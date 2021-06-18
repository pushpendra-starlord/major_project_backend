from django.urls import path
from blog.views import BlogPostView,LikeView,CommentView,ListBlogView, UnlikePost

urlpatterns=[
    path("post/list/",ListBlogView.as_view()),
    path("post/",BlogPostView.as_view()),
    path("like/<int:id>/",LikeView.as_view()),
    path("comment/<int:id>/",CommentView.as_view()),
    path("comment/",CommentView.as_view()),
    path('unlike/' , UnlikePost.as_view())
   
]