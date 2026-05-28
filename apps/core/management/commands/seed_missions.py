"""Seed daily missions."""

from django.core.management.base import BaseCommand

from apps.core.models import DailyMission


class Command(BaseCommand):
    """Seed daily missions command."""

    help = "Seed the database with daily missions"

    def handle(self, *args, **options) -> None:
        """Seed daily missions."""
        missions_data = [
            {
                "mission_type": "daily_login",
                "title": "Primer Paso",
                "description": "Inicia sesión en el juego",
                "target": 1,
                "energy_reward": 3,
            },
            {
                "mission_type": "first_pull",
                "title": "Primera Invocación",
                "description": "Realiza tu primera invocación del día",
                "target": 1,
                "energy_reward": 5,
            },
            {
                "mission_type": "gacha_pulls",
                "title": "Aventurero",
                "description": "Realiza 5 invocaciones",
                "target": 5,
                "energy_reward": 15,
            },
            {
                "mission_type": "win_battles",
                "title": "Guerrero Victorioso",
                "description": "Gana 3 batallas",
                "target": 3,
                "energy_reward": 10,
            },
            {
                "mission_type": "level_up_god",
                "title": "Entrenamiento",
                "description": "Sube de nivel a 2 dioses",
                "target": 2,
                "energy_reward": 8,
            },
            {
                "mission_type": "ascend_god",
                "title": "Ascensión Divina",
                "description": "Asciende a un dios a siguiente tier",
                "target": 1,
                "energy_reward": 20,
            },
            {
                "mission_type": "equip_item",
                "title": "Equipando Poder",
                "description": "Equipa 3 objetos",
                "target": 3,
                "energy_reward": 8,
            },
            {
                "mission_type": "win_campaign",
                "title": "Conquistador",
                "description": "Completa 2 niveles de campaña",
                "target": 2,
                "energy_reward": 12,
            },
        ]

        created_count = 0
        for mission_data in missions_data:
            mission, created = DailyMission.objects.update_or_create(
                mission_type=mission_data["mission_type"],
                defaults=mission_data,
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Created mission: {mission.title}")
                )
            else:
                self.stdout.write(f"Updated mission: {mission.title}")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone! Created {created_count} new missions, "
                f"total missions: {DailyMission.objects.count()}"
            )
        )
