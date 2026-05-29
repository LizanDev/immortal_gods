"""Reset daily missions: randomize active set and clear player progress."""

import random
from datetime import UTC, date, datetime, time, timedelta

from django.core.management.base import BaseCommand

from apps.core.models import DailyMission, MissionResetLog, PlayerMission

PICK_COUNT = 5


class Command(BaseCommand):
    """Reset daily missions command."""

    help = "Randomize active daily missions, reset all player progress"

    def add_arguments(self, parser) -> None:
        """Add arguments."""
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be done without making changes",
        )

    def handle(self, *args, **options) -> None:
        """Randomize and reset."""
        dry_run = options.get("dry_run", False)

        pool = list(DailyMission.objects.filter(in_pool=True))
        if len(pool) < PICK_COUNT:
            self.stdout.write(
                self.style.WARNING(
                    f"Pool only has {len(pool)} missions; need at least {PICK_COUNT}. "
                    "Run seed_mission_pool first."
                )
            )
            return

        chosen = random.sample(pool, PICK_COUNT)
        chosen_ids = [m.id for m in chosen]

        if dry_run:
            self.stdout.write("Dry run — would activate:")
            for m in chosen:
                self.stdout.write(
                    f"  [{m.mission_type}] {m.title} — {m.description} "
                    f"({m.target}x, {m.gem_reward} gemas)"
                )
            return

        # Deactivate all, activate chosen
        DailyMission.objects.filter(in_pool=True).update(is_active=False)
        DailyMission.objects.filter(id__in=chosen_ids).update(is_active=True)

        # Reset all player progress
        deleted = PlayerMission.objects.all().delete()[0]

        # Update reset log
        log = MissionResetLog.objects.first()
        if log:
            log.last_reset = datetime.now(UTC)
            log.save(update_fields=["last_reset"])
        else:
            MissionResetLog.objects.create()

        self.stdout.write(
            self.style.SUCCESS(f"Activated {PICK_COUNT} missions for today:")
        )
        for m in chosen:
            self.stdout.write(
                f"  ✅ [{m.mission_type}] {m.title} ({m.target}x, {m.gem_reward} gemas)"
            )
        self.stdout.write(
            self.style.SUCCESS(f"Deleted {deleted} stale player mission records")
        )


def needs_reset() -> bool:
    """Check if missions need to be reset (past 2 AM and not yet done today)."""
    now = datetime.now(UTC)
    today_2am = datetime.combine(date.today(), time(2, 0), tzinfo=UTC)

    if now < today_2am:
        return False

    log = MissionResetLog.objects.first()
    if not log:
        return True

    return log.last_reset < today_2am - timedelta(hours=1)
