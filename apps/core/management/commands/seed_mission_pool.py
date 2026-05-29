"""Seed a large pool of daily mission variants for randomization."""

from django.core.management.base import BaseCommand

from apps.core.models import DailyMission

MISSION_POOL = [
    # daily_login (3 variants)
    {
        "mission_type": "daily_login",
        "title": "Primer Paso",
        "description": "Inicia sesión en el juego",
        "target": 1,
        "gem_reward": 6,
    },
    {
        "mission_type": "daily_login",
        "title": "Rutina Diaria",
        "description": "Inicia sesión para reclamar tu recompensa",
        "target": 1,
        "gem_reward": 8,
    },
    {
        "mission_type": "daily_login",
        "title": "Bienvenido",
        "description": "Entra al juego y prepara tu equipo",
        "target": 1,
        "gem_reward": 5,
    },
    # first_pull (2 variants)
    {
        "mission_type": "first_pull",
        "title": "Primera Invocación",
        "description": "Realiza tu primera invocación del día",
        "target": 1,
        "gem_reward": 10,
    },
    {
        "mission_type": "first_pull",
        "title": "Llamado Divino",
        "description": "Invoca un dios por primera vez hoy",
        "target": 1,
        "gem_reward": 12,
    },
    # gacha_pulls (3 variants)
    {
        "mission_type": "gacha_pulls",
        "title": "Aventurero",
        "description": "Realiza 5 invocaciones",
        "target": 5,
        "gem_reward": 30,
    },
    {
        "mission_type": "gacha_pulls",
        "title": "Invocador Frenético",
        "description": "Realiza 10 invocaciones",
        "target": 10,
        "gem_reward": 35,
    },
    {
        "mission_type": "gacha_pulls",
        "title": "Coleccionista",
        "description": "Realiza 3 invocaciones",
        "target": 3,
        "gem_reward": 18,
    },
    # win_battles (3 variants)
    {
        "mission_type": "win_battles",
        "title": "Guerrero Victorioso",
        "description": "Gana 3 batallas",
        "target": 3,
        "gem_reward": 20,
    },
    {
        "mission_type": "win_battles",
        "title": "Imparable",
        "description": "Gana 5 batallas",
        "target": 5,
        "gem_reward": 30,
    },
    {
        "mission_type": "win_battles",
        "title": "Desafío de Combate",
        "description": "Gana 2 batallas PvP o de campaña",
        "target": 2,
        "gem_reward": 14,
    },
    # level_up_god (3 variants)
    {
        "mission_type": "level_up_god",
        "title": "Entrenamiento",
        "description": "Sube de nivel a 2 dioses",
        "target": 2,
        "gem_reward": 16,
    },
    {
        "mission_type": "level_up_god",
        "title": "Maestro Entrenador",
        "description": "Sube de nivel a 5 dioses",
        "target": 5,
        "gem_reward": 28,
    },
    {
        "mission_type": "level_up_god",
        "title": "Disciplina",
        "description": "Sube de nivel a 1 dios",
        "target": 1,
        "gem_reward": 8,
    },
    # ascend_god (2 variants)
    {
        "mission_type": "ascend_god",
        "title": "Ascensión Divina",
        "description": "Asciende a un dios a siguiente tier",
        "target": 1,
        "gem_reward": 40,
    },
    {
        "mission_type": "ascend_god",
        "title": "Poder Superior",
        "description": "Asciende a 2 dioses",
        "target": 2,
        "gem_reward": 50,
    },
    # equip_item (3 variants)
    {
        "mission_type": "equip_item",
        "title": "Equipando Poder",
        "description": "Equipa 3 objetos",
        "target": 3,
        "gem_reward": 16,
    },
    {
        "mission_type": "equip_item",
        "title": "Bien Equipado",
        "description": "Equipa 5 objetos",
        "target": 5,
        "gem_reward": 22,
    },
    {
        "mission_type": "equip_item",
        "title": "Forjando el Set",
        "description": "Equipa 2 objetos a un mismo dios",
        "target": 2,
        "gem_reward": 12,
    },
    # win_campaign (3 variants)
    {
        "mission_type": "win_campaign",
        "title": "Conquistador",
        "description": "Completa 2 niveles de campaña",
        "target": 2,
        "gem_reward": 25,
    },
    {
        "mission_type": "win_campaign",
        "title": "Héroe de Campaña",
        "description": "Completa 4 niveles de campaña",
        "target": 4,
        "gem_reward": 40,
    },
    {
        "mission_type": "win_campaign",
        "title": "Explorador",
        "description": "Completa 1 nivel de campaña",
        "target": 1,
        "gem_reward": 12,
    },
]


class Command(BaseCommand):
    """Seed mission pool command."""

    help = "Seed the database with a pool of mission variants for daily randomization"

    def handle(self, *args, **options) -> None:
        """Seed mission pool."""
        # Clear existing missions
        DailyMission.objects.all().delete()

        created = 0
        for data in MISSION_POOL:
            DailyMission.objects.create(
                mission_type=data["mission_type"],
                title=data["title"],
                description=data["description"],
                target=data["target"],
                gem_reward=data["gem_reward"],
                is_active=True,
                in_pool=True,
            )
            created += 1
            self.stdout.write(self.style.SUCCESS(f"Created: {data['title']}"))

        self.stdout.write(
            self.style.SUCCESS(f"\nDone! Created {created} mission variants in pool")
        )
