from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth import get_user_model
import os
from dotenv import load_dotenv

from RBAC.settings import EMAIL_HOST_USER
load_dotenv()

class PasswordResetHandler:
    @staticmethod
    def send_reset_email(user, uid, token):
        subject = 'Password Reset Request'
        message = (
            f'Please use the following link to reset your password:\n\n'
            f'http://127.0.0.1:8000/users/password-reset/{uid}/{token}/'
        )
        from_email = EMAIL_HOST_USER
        to_email = user.email
        send_mail(subject, message, from_email, [to_email])

    @staticmethod
    def reset_password(uid, token, new_password):
        User = get_user_model()
        try:
            uid = urlsafe_base64_encode(uid).decode()
            user = User.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                return True, "Password reset successful"
            else:
                return False, "Invalid token"
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return False, "Invalid user id"
