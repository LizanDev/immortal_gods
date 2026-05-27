"""Management command to unlock campaign levels."""

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from apps.core.models import PlayerProfile


class Command(BaseCommand):
    """Unlock all campaign levels for a user."""

    help = "Unlock all campaign levels for a user"

    def add_arguments(self, parser):
        parser.add_argument("--username", type=str, help="Username to unlock")

    def handle(self, *args, **options):
        username = options.get("username")
        if username:
            try:
                user = User.objects.get(username=username)
                profile = user.profile
                profile.campaign_progress = 15
                profile.save(update_fields=["campaign_progress"])
                self.stdout.write(
                    self.style.SUCCESS(f"Unlocked all levels for {username}")
                )
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"User {username} not found"))
        else:
            PlayerProfile.objects.update(campaign_progress=15)
            self.stdout.write(self.style.SUCCESS("Unlocked all levels for all users"))
