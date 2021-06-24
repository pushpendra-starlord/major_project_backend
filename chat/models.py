from authentication.models import User
from chat.managers import ThreadManager
from django.db import models
from django.utils import timezone

class TrackingModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Thread(TrackingModel):
    THREAD_TYPE = (
        ('personal', 'Personal'),
        ('group', 'Group')
    )

    name = models.CharField(max_length=50, null=True, blank=True)
    thread_type = models.CharField(max_length=15, choices=THREAD_TYPE, default='group')
    users = models.ManyToManyField('authentication.User')
    last_message = models.DateTimeField(default= timezone.now)

    objects = ThreadManager()

    def __str__(self) -> str:
        if self.thread_type == 'personal' and self.users.count() == 2:
            return f'{self.users.first()} and {self.users.last()}'
        return f'{self.name}'

class Message(TrackingModel):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    sender = models.ForeignKey('authentication.User', on_delete=models.CASCADE)
    text = models.TextField(blank=False, null=False)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'From <Thread - {self.thread}>'

    def get_sender_user(self):
        sender = self.sender
        if sender:
            return sender.username
        return ''

class InScreenHistory(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    in_screen = models.BooleanField(default=False)

