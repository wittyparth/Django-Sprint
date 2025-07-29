from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from users.models import Profile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

# signals.py
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.mail import send_mail
from django.conf import settings
from users.models import User
from config.utils import generate_verification_token

@receiver(post_save, sender=User)
def send_verification_email(sender, instance, created, **kwargs):
    if created and not instance.is_active:
        token = generate_verification_token(instance.id)
        link = f"{settings.FRONTEND_URL}/verify-email/{token}"
        
        send_mail(
            subject="Verify your email",
            message=f"Click the link to verify your account: {link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.email],
            fail_silently=False,
        )

from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from users.models import Profile



def send_password_reset_email(user,token):
    
    link = f"{settings.FRONTEND_URL}/reset-password/{token}"
    send_mail(
        subject="Reset your password",
        message=f"Click the link to reset your password: {link}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        from users.models import Profile  # avoid circular imports
        Profile.objects.create(user=instance)