"""Reset daily missions progress."""

from django.core.management.base import BaseCommand

from apps.core.models import PlayerMission


class Command(BaseCommand):
    """Reset daily missions command."""

    help = "Reset all player mission progress (for daily reset)"

    def add_arguments(self, parser) -> None:
        """Add arguments."""
        parser.add_argument(
            "--all",
            action="store_true",
            help="Also reset claimed status",
        )

    def handle(self, *args, **options) -> None:
        """Reset missions."""
        reset_all = options.get("all", False)

        if reset_all:
            count = PlayerMission.objects.all().count()
            PlayerMission.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(f"Deleted all {count} player mission records")
            )
        else:
            count = PlayerMission.objects.filter(claimed=False).count()
            PlayerMission.objects.filter(claimed=False).update(
                progress=0, completed=False
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Reset {count} unclaimed missions (progress set to 0)"
                )
            )
