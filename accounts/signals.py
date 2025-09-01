# signals.py
import random
from django.core.mail import send_mail
from django.dispatch import receiver
from djoser.signals import user_registered
from .models import EmailVerification

@receiver(user_registered)
def send_verification_code(user, request, **kwargs):
    code = str(random.randint(100000, 999999))
    EmailVerification.objects.update_or_create(user=user, defaults={'code': code})

    send_mail(
        subject='Your Verification Code',
        message=f'Your verification code is: {code}',
        from_email='noreply@example.com',
        recipient_list=[user.email],
    )
