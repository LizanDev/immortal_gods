"""Seed enemy team data for all campaign levels."""

from django.core.management.base import BaseCommand

from apps.campaign.models import CampaignLevel

ENEMY_POOL = [
    {"name": "Soldado Esqueleto", "role": "Tank", "base_atk": 40, "base_def": 60},
    {"name": "Arquero Fantasma", "role": "Archer", "base_atk": 55, "base_def": 35},
    {"name": "Mago Oscuro", "role": "Mage", "base_atk": 60, "base_def": 30},
    {"name": "Lobo de Sombra", "role": "Assassin", "base_atk": 65, "base_def": 25},
    {"name": "Gólem de Piedra", "role": "Tank", "base_atk": 35, "base_def": 75},
    {"name": "Harpía", "role": "Archer", "base_atk": 50, "base_def": 30},
    {"name": "Quimera", "role": "Mage", "base_atk": 55, "base_def": 40},
    {"name": "Minotauro", "role": "Tank", "base_atk": 50, "base_def": 65},
    {"name": "Súcubo", "role": "Assassin", "base_atk": 60, "base_def": 30},
    {"name": "Centauro", "role": "Archer", "base_atk": 55, "base_def": 40},
    {"name": "Gorgona", "role": "Support", "base_atk": 40, "base_def": 50},
    {"name": "Hidra", "role": "Mage", "base_atk": 65, "base_def": 45},
    {"name": "Cerbero", "role": "Tank", "base_atk": 55, "base_def": 70},
    {"name": "Pegaso Oscuro", "role": "Support", "base_atk": 45, "base_def": 45},
    {"name": "Dragón Menor", "role": "Mage", "base_atk": 70, "base_def": 40},
    {"name": "Titán", "role": "Tank", "base_atk": 60, "base_def": 80},
]

BOSS_POOL = [
    {"name": "Rey Momia", "role": "Tank", "base_atk": 70, "base_def": 90},
    {"name": "Sacerdote de Seth", "role": "Mage", "base_atk": 85, "base_def": 55},
    {"name": "Hefesto Enfurecido", "role": "Tank", "base_atk": 75, "base_def": 95},
    {"name": "Hades Renacido", "role": "Assassin", "base_atk": 90, "base_def": 60},
    {"name": "Thor de las Tormentas", "role": "Tank", "base_atk": 80, "base_def": 85},
    {"name": "Emperador de Jade", "role": "Mage", "base_atk": 95, "base_def": 65},
    {"name": "Dragón Celestial", "role": "Mage", "base_atk": 100, "base_def": 70},
    {"name": "Eclipse Viviente", "role": "Assassin", "base_atk": 105, "base_def": 75},
    {"name": "Vacío Absoluto", "role": "Mage", "base_atk": 120, "base_def": 80},
]

LEVEL_SCALING = {
    "easy": {"num_enemies": 3, "scaling": 0.04, "hp_mult": 10},
    "normal": {"num_enemies": 3, "scaling": 0.07, "hp_mult": 12},
    "hard": {"num_enemies": 4, "scaling": 0.10, "hp_mult": 14},
    "hell": {"num_enemies": 4, "scaling": 0.14, "hp_mult": 16},
}


def build_enemy_team(level: CampaignLevel) -> list[dict]:
    """Build enemy team data for a campaign level."""
    diff = level.difficulty
    config = LEVEL_SCALING.get(diff, LEVEL_SCALING["easy"])
    num_enemies = 5 if level.is_boss_level else config["num_enemies"]
    scaling = config["scaling"]

    pool = BOSS_POOL if level.is_boss_level else ENEMY_POOL
    base_power = level.required_power // num_enemies
    level_mult = 1.0 + (level.order * scaling)

    enemies = []
    for i in range(num_enemies):
        template = pool[i % len(pool)]
        atk = int((template["base_atk"] + base_power * 0.3) * level_mult)
        def_ = int((template["base_def"] + base_power * 0.2) * level_mult)
        base_hp = template.get("base_hp", 200)
        hp = int((base_hp + base_power) * config["hp_mult"] * level_mult)
        speed_mult = 1.0 + (level.order * 0.02)
        speed = int((60 + (i * 5)) * speed_mult)

        enemies.append({
            "name": template["name"],
            "role": template["role"],
            "attack": atk,
            "defense": def_,
            "hp": hp,
            "speed": speed,
        })

    return enemies


class Command(BaseCommand):
    """Seed enemy team data for all campaign levels."""

    help = "Generates enemy team data for each campaign level"

    def handle(self, *args, **options):
        levels = CampaignLevel.objects.all().order_by("order")
        updated = 0
        for level in levels:
            level.enemy_team_data = build_enemy_team(level)
            level.save(update_fields=["enemy_team_data"])
            updated += 1
            enemy_count = len(level.enemy_team_data)
            msg = f"  Level {level.order}: {level.name} ({enemy_count} enemies)"
            self.stdout.write(msg)

        success_msg = f"Seeded {updated} campaign levels"
        self.stdout.write(self.style.SUCCESS(success_msg))
