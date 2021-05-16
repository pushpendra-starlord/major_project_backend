from django.contrib import admin
from .models import BlogPost, Like, Comment
# Register your models here.
admin.site.register(BlogPost)
admin.site.register(Like)
admin.site.register(Comment)