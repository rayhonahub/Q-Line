from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """User сохта шуд → Profile автоматӣ месозем"""
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """User сабт шуд → Profile ҳам сабт мешавад"""
    if hasattr(instance, 'profile'):
        instance.profile.save()