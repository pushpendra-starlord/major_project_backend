from django.contrib import admin
from chat.models import Message, Thread, InScreenHistory


# class MessageInline(admin.StackedInline):
#     model = Message
#     fields = ('sender', 'text', )
#     readonly_fields = ('sender', 'text', 'timestamp',)


# class ThreadAdmin(admin.ModelAdmin):
#     model = Thread
#     inlines = (MessageInline,)

admin.site.register(Thread)
admin.site.register(Message)
admin.site.register(InScreenHistory)