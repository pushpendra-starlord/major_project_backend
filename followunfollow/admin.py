from django.contrib import admin
from .models import Follow, BlockList

# Register your models here.
admin.site.register(Follow)
admin.site.register(BlockList)