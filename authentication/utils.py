from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from followunfollow.models import Follow

def get_token(user_object):
    refresh = RefreshToken.for_user(user_object)
    token = {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
    return token


def otp_creation(user):
    otp_code = get_random_string(length=6, allowed_chars='1234567890')
    user.otp_code = otp_code
    user.otp_created_at = timezone.now()
    user.save()

    subject = 'Account Verification'
    message = f'Hi {user.username}, This mail consist of otp code please enter the otp code for verification of your account. OTP {otp_code} '
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email, ]
    send_mail( subject, message, email_from, recipient_list)

def get_following_count(user):
    follower_obj = Follow.objects.filter(user = user)
    follower = follower_obj.values_list('follower', flat= True).count()
    following = follower_obj.values_list('following', flat= True).count()
    
    return {
        "follower" : follower,
        "following": following 
    }

