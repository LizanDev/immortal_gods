"""Context processors for core app."""

from .models import GiftNotification


def gift_notifications(request):
    """Inject unread gift notifications into template context."""
    if not request.user.is_authenticated:
        return {}
    try:
        profile = request.user.profile
        notifications = list(
            GiftNotification.objects.filter(player=profile, seen=False)[:5]
        )
        return {"gift_notifications": notifications}
    except Exception:
        return {}
