"""Seed enemy team data for all campaign levels."""

import urllib.parse

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


QUALITY_ROMAN = {"easy": "I", "normal": "II", "hard": "III", "hell": "IV"}

ROLE_EMOJI = {
    "Tank": "🛡️",
    "Archer": "🏹",
    "Mage": "🔮",
    "Assassin": "🗡️",
    "Support": "✨",
}

ENEMY_PROMPTS = {
    "Soldado Esqueleto": "Skeleton warrior, red eyes, rusty armor, dark fantasy battlefield",  # noqa: E501
    "Arquero Fantasma": "Ghostly ethereal archer floating in mist, spectral bow, dark fantasy",  # noqa: E501
    "Mago Oscuro": "Dark wizard with flowing black robes, glowing purple magic, ancient temple",  # noqa: E501
    "Lobo de Sombra": "Giant shadow wolf with glowing blue eyes, ethereal black fur, fantasy art",  # noqa: E501
    "Gólem de Piedra": "Massive stone golem covered in moss, glowing orange cracks, epic fantasy",  # noqa: E501
    "Harpía": "Half-woman half-bird harpy, grey feather wings, perched on ancient ruins",  # noqa: E501
    "Quimera": "Mythical chimera, lion head goat body serpent tail, breathing fire",  # noqa: E501
    "Minotauro": "Bull-headed minotaur wielding massive battle axe, stone labyrinth",  # noqa: E501
    "Súcubo": "Winged demoness with deep red skin, glowing eyes, gothic fantasy portrait",  # noqa: E501
    "Centauro": "Powerful centaur archer, drawn bow, ancient forest clearing",  # noqa: E501
    "Gorgona": "Medusa-like gorgon with living snake hair, green eyes, Greek ruins",  # noqa: E501
    "Hidra": "Multi-headed hydra rising from swamp, sharp fangs, dark marshland",  # noqa: E501
    "Cerbero": "Three-headed hellhound with black fur, chains, fiery underworld gates",  # noqa: E501
    "Pegaso Oscuro": "Black winged horse with purple aura, starry mane, storm clouds",  # noqa: E501
    "Dragón Menor": "Young dragon with dark scales, tattered wings, treasure hoard",  # noqa: E501
    "Titán": "Colossal armored titan wielding stone club, mountainous landscape",  # noqa: E501
    "Rey Momia": "Ancient mummy king in gold and lapis lazuli, glowing eyes, Egyptian tomb",  # noqa: E501
    "Sacerdote de Seth": "Dark priest with jackal mask, crimson robes, sandstorm magic",  # noqa: E501
    "Hefesto Enfurecido": "Furious fire god, metallic skin, lava beard, volcanic forge",  # noqa: E501
    "Hades Renacido": "Hades lord of underworld, ethereal crown, blue flame, souls",  # noqa: E501
    "Thor de las Tormentas": "Thor storm god with crackling lightning Mjolnir, thunder sky",  # noqa: E501
    "Emperador de Jade": "Jade emperor in ornate Chinese robes, green aura, celestial dragon",  # noqa: E501
    "Dragón Celestial": "Celestial dragon made of stars and nebula, floating through cosmos",  # noqa: E501
    "Eclipse Viviente": "Living eclipse being of pure darkness with corona of light",  # noqa: E501
    "Vacío Absoluto": "Void entity of nothingness, swirling dark matter, cosmic entity",  # noqa: E501
}


def build_enemy_team(level: CampaignLevel) -> list[dict]:
    """Build enemy team data for a campaign level."""
    diff = level.difficulty
    config = LEVEL_SCALING.get(diff, LEVEL_SCALING["easy"])
    num_enemies = 5 if level.is_boss_level else config["num_enemies"]
    quality = QUALITY_MULT.get(diff, 1.0)
    diff_pct = config["diff_pct"]

    pool = BOSS_POOL if level.is_boss_level else ENEMY_POOL
    display_level = level.order * 2
    level_mult = 1.0 + (display_level * 0.1)
    quality_roman = QUALITY_ROMAN[diff]

    enemies = []
    for i in range(num_enemies):
        template = pool[i % len(pool)]
        atk = int(template["base_atk"] * quality * level_mult * diff_pct)
        def_ = int(template["base_def"] * quality * level_mult * diff_pct)
        base_hp = (template["base_atk"] + template["base_def"]) * 2
        hp = int(base_hp * quality * level_mult * diff_pct * config["hp_mult"] // 10)
        speed = int((60 + (i * 5)) * (1 + level.order * 0.03))
        prompt = ENEMY_PROMPTS.get(
            template["name"], f"epic fantasy {template['role']} monster"
        )  # noqa: E501
        seed = abs(hash(template["name"])) % 10000
        image_url = (
            f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}"
            f"?width=400&height=300&nologo=true&seed={seed}&model=flux"
        )

        enemies.append(
            {
                "name": template["name"],
                "role": template["role"],
                "attack": atk,
                "defense": def_,
                "hp": hp,
                "speed": speed,
                "level": display_level,
                "quality_roman": quality_roman,
                "image_url": image_url,
            }
        )

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
