"""Core signals."""

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.core.models import PlayerProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a PlayerProfile when a new user is created."""
    if created:
        PlayerProfile.objects.create(user=instance)
