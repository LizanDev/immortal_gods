"""Seed enemy team data for all campaign levels."""

from django.core.management.base import BaseCommand

from apps.campaign.models import CampaignLevel

ENEMY_POOL = [
    {"name": "Soldado Esqueleto", "role": "Tank", "base_atk": 95, "base_def": 145},
    {"name": "Arquero Fantasma", "role": "Archer", "base_atk": 130, "base_def": 85},
    {"name": "Mago Oscuro", "role": "Mage", "base_atk": 145, "base_def": 75},
    {"name": "Lobo de Sombra", "role": "Assassin", "base_atk": 155, "base_def": 65},
    {"name": "Gólem de Piedra", "role": "Tank", "base_atk": 85, "base_def": 170},
    {"name": "Harpía", "role": "Archer", "base_atk": 120, "base_def": 80},
    {"name": "Quimera", "role": "Mage", "base_atk": 140, "base_def": 95},
    {"name": "Minotauro", "role": "Tank", "base_atk": 110, "base_def": 155},
    {"name": "Súcubo", "role": "Assassin", "base_atk": 145, "base_def": 80},
    {"name": "Centauro", "role": "Archer", "base_atk": 135, "base_def": 95},
    {"name": "Gorgona", "role": "Support", "base_atk": 95, "base_def": 120},
    {"name": "Hidra", "role": "Mage", "base_atk": 155, "base_def": 105},
    {"name": "Cerbero", "role": "Tank", "base_atk": 120, "base_def": 165},
    {"name": "Pegaso Oscuro", "role": "Support", "base_atk": 105, "base_def": 110},
    {"name": "Dragón Menor", "role": "Mage", "base_atk": 165, "base_def": 100},
    {"name": "Titán", "role": "Tank", "base_atk": 130, "base_def": 185},
]

BOSS_POOL = [
    {"name": "Rey Momia", "role": "Tank", "base_atk": 160, "base_def": 220},
    {"name": "Sacerdote de Seth", "role": "Mage", "base_atk": 200, "base_def": 130},
    {"name": "Hefesto Enfurecido", "role": "Tank", "base_atk": 170, "base_def": 240},
    {"name": "Hades Renacido", "role": "Assassin", "base_atk": 210, "base_def": 140},
    {"name": "Thor de las Tormentas", "role": "Tank", "base_atk": 180, "base_def": 210},
    {"name": "Emperador de Jade", "role": "Mage", "base_atk": 230, "base_def": 150},
    {"name": "Dragón Celestial", "role": "Mage", "base_atk": 240, "base_def": 160},
    {"name": "Eclipse Viviente", "role": "Assassin", "base_atk": 260, "base_def": 170},
    {"name": "Vacío Absoluto", "role": "Mage", "base_atk": 280, "base_def": 190},
]

LEVEL_SCALING = {
    "easy": {"num_enemies": 3, "hp_mult": 10, "diff_pct": 0.70},
    "normal": {"num_enemies": 3, "hp_mult": 14, "diff_pct": 0.85},
    "hard": {"num_enemies": 4, "hp_mult": 18, "diff_pct": 1.00},
    "hell": {"num_enemies": 4, "hp_mult": 22, "diff_pct": 1.20},
}

QUALITY_MULT = {"easy": 1.00, "normal": 1.15, "hard": 1.30, "hell": 1.45}


def build_enemy_team(level: CampaignLevel) -> list[dict]:
    """Build enemy team data for a campaign level."""
    diff = level.difficulty
    config = LEVEL_SCALING.get(diff, LEVEL_SCALING["easy"])
    num_enemies = 5 if level.is_boss_level else config["num_enemies"]
    quality = QUALITY_MULT.get(diff, 1.0)
    diff_pct = config["diff_pct"]

    pool = BOSS_POOL if level.is_boss_level else ENEMY_POOL
    enemy_level = level.order * 2
    level_mult = 1.0 + (enemy_level * 0.1)

    enemies = []
    for i in range(num_enemies):
        template = pool[i % len(pool)]
        atk = int(template["base_atk"] * quality * level_mult * diff_pct)
        def_ = int(template["base_def"] * quality * level_mult * diff_pct)
        base_hp = (template["base_atk"] + template["base_def"]) * 2
        hp = int(base_hp * quality * level_mult * diff_pct * config["hp_mult"] // 10)
        speed = int((60 + (i * 5)) * (1 + level.order * 0.03))

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
