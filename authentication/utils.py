from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail

def get_token(user_object):
    refresh = RefreshToken.for_user(user_object)
    token = {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
    return token


def otp_creation(user):
    otp_code = get_random_string(length=6, allowed_chars='1234567890')
    user.update(otp_code = otp_code, otp_created_at = timezone.now())

    subject = 'Account Verification'
    message = f'Hi {user.username}, This mail consist of otp code please enter the otp code for verification of your account. OTP {otp_code} '
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email, ]
    send_mail( subject, message, email_from, recipient_list)

