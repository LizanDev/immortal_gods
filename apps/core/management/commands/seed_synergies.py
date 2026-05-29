"""Management command to seed synergy tags and rebalance god rarities."""

from django.core.management.base import BaseCommand

from apps.gods.models import God, GodSynergyTag, Rarity

SYNERGY_TAGS_DATA: dict[str, list[str]] = {
    # Greek
    "Zeus": ["sky", "thunder"],
    "Hades": ["death", "king"],
    "Poseidon": ["sea", "earth"],
    "Athena": ["wisdom", "war"],
    "Apollo": ["sun", "wisdom"],
    "Ares": ["war", "strength"],
    "Artemis": ["moon", "hunt"],
    "Hermes": ["messenger", "trickery"],
    "Hephaestus": ["forge", "earth"],
    "Demeter": ["nature", "wealth"],
    "Dionysus": ["nature", "magic"],
    "Persephone": ["death", "nature"],
    "Hecate": ["magic", "moon"],
    "Eros": ["love", "trickery"],
    "Nike": ["war", "messenger"],
    "Cronus": ["king", "strength"],
    "Gaia": ["earth", "nature"],
    "Prometheus": ["forge", "trickery"],
    "Morpheus": ["fate", "magic"],
    # Aztec
    "Huitzilopochtli": ["war", "sun"],
    "Quetzalcoatl": ["wisdom", "sky"],
    "Tezcatlipoca": ["trickery", "fate"],
    "Tlaloc": ["thunder", "nature"],
    "Xipe Totec": ["earth", "nature"],
    "Coatlicue": ["earth", "death"],
    "Mictlantecuhtli": ["death", "king"],
    "Xochiquetzal": ["love", "nature"],
    "Xiuhtecuhtli": ["forge", "sun"],
    "Coyolxauhqui": ["moon", "war"],
    "Ehecatl": ["messenger", "sky"],
    "Tonatiuh": ["sun", "strength"],
    # Chinese
    "Jade Emperor": ["sky", "king"],
    "Sun Wukong": ["trickery", "strength"],
    "Nezha": ["war", "strength"],
    "Erlang Shen": ["war", "wisdom"],
    "Chang'e": ["moon", "love"],
    "Dragon King": ["sea", "king"],
    "Guan Yu": ["war", "justice"],
    "Nuwa": ["earth", "magic"],
    "Zhong Kui": ["death", "guardian"],
    "Caishen": ["wealth", "fate"],
    "Fuxi": ["wisdom", "fate"],
    "Shennong": ["healing", "nature"],
    "Xiwangmu": ["healing", "wisdom"],
    "Huangdi": ["king", "war"],
    "Lei Gong": ["thunder", "justice"],
    # Egyptian
    "Ra": ["sun", "king"],
    "Osiris": ["death", "king"],
    "Anubis": ["death", "guardian"],
    "Horus": ["sky", "war"],
    "Isis": ["magic", "healing"],
    "Set": ["trickery", "strength"],
    "Thoth": ["wisdom", "messenger"],
    "Sekhmet": ["war", "strength"],
    "Bastet": ["love", "guardian"],
    "Ptah": ["forge", "creation"],
    "Amun": ["sky", "king"],
    "Hathor": ["love", "family"],
    "Khepri": ["sun", "nature"],
    "Ma'at": ["justice", "fate"],
    "Sobek": ["strength", "sea"],
    "Seshat": ["wisdom", "fate"],
    # Nordic
    "Odin": ["wisdom", "king"],
    "Thor": ["thunder", "strength"],
    "Loki": ["trickery", "magic"],
    "Freya": ["love", "magic"],
    "Tyr": ["war", "justice"],
    "Heimdall": ["guardian", "messenger"],
    "Frigg": ["family", "fate"],
    "Baldr": ["sun", "healing"],
    "Skadi": ["hunt", "earth"],
    "Vidar": ["strength", "earth"],
    "Ymir": ["earth", "strength"],
    "Hel": ["death", "king"],
    "Njord": ["sea", "wealth"],
    "Sif": ["nature", "family"],
    "Ullr": ["hunt", "messenger"],
    "Bragi": ["wisdom", "magic"],
}

RARITY_REBALANCE: dict[str, str] = {
    # Greek — 1 mythic, 4 legendary, 6 epic, 4 rare, 4 common
    "Zeus": Rarity.MYTHIC,
    "Hades": Rarity.LEGENDARY,
    "Poseidon": Rarity.LEGENDARY,
    "Athena": Rarity.LEGENDARY,
    "Apollo": Rarity.LEGENDARY,
    "Ares": Rarity.EPIC,
    "Artemis": Rarity.EPIC,
    "Hermes": Rarity.EPIC,
    "Hephaestus": Rarity.EPIC,
    "Demeter": Rarity.EPIC,
    "Dionysus": Rarity.EPIC,
    "Persephone": Rarity.RARE,
    "Hecate": Rarity.RARE,
    "Eros": Rarity.RARE,
    "Nike": Rarity.RARE,
    "Cronus": Rarity.COMMON,
    "Gaia": Rarity.COMMON,
    "Prometheus": Rarity.COMMON,
    "Morpheus": Rarity.COMMON,
    # Aztec — 1 mythic, 3 legendary, 4 epic, 4 rare
    "Huitzilopochtli": Rarity.MYTHIC,
    "Quetzalcoatl": Rarity.LEGENDARY,
    "Tezcatlipoca": Rarity.LEGENDARY,
    "Coatlicue": Rarity.LEGENDARY,
    "Tlaloc": Rarity.EPIC,
    "Xipe Totec": Rarity.EPIC,
    "Mictlantecuhtli": Rarity.EPIC,
    "Xiuhtecuhtli": Rarity.EPIC,
    "Xochiquetzal": Rarity.RARE,
    "Coyolxauhqui": Rarity.RARE,
    "Ehecatl": Rarity.RARE,
    "Tonatiuh": Rarity.RARE,
    # Chinese — 1 mythic, 4 legendary, 5 epic, 3 rare, 2 common
    "Jade Emperor": Rarity.MYTHIC,
    "Sun Wukong": Rarity.LEGENDARY,
    "Dragon King": Rarity.LEGENDARY,
    "Xiwangmu": Rarity.LEGENDARY,
    "Huangdi": Rarity.LEGENDARY,
    "Nezha": Rarity.EPIC,
    "Erlang Shen": Rarity.EPIC,
    "Guan Yu": Rarity.EPIC,
    "Nuwa": Rarity.EPIC,
    "Lei Gong": Rarity.EPIC,
    "Chang'e": Rarity.RARE,
    "Zhong Kui": Rarity.RARE,
    "Fuxi": Rarity.RARE,
    "Caishen": Rarity.COMMON,
    "Shennong": Rarity.COMMON,
    # Egyptian — 1 mythic, 4 legendary, 6 epic, 3 rare, 2 common
    "Ra": Rarity.MYTHIC,
    "Osiris": Rarity.LEGENDARY,
    "Amun": Rarity.LEGENDARY,
    "Hathor": Rarity.LEGENDARY,
    "Khepri": Rarity.LEGENDARY,
    "Anubis": Rarity.EPIC,
    "Horus": Rarity.EPIC,
    "Isis": Rarity.EPIC,
    "Ma'at": Rarity.EPIC,
    "Sobek": Rarity.EPIC,
    "Sekhmet": Rarity.EPIC,
    "Set": Rarity.RARE,
    "Thoth": Rarity.RARE,
    "Seshat": Rarity.RARE,
    "Bastet": Rarity.COMMON,
    "Ptah": Rarity.COMMON,
    # Nordic — 1 mythic, 4 legendary, 6 epic, 3 rare, 2 common
    "Odin": Rarity.MYTHIC,
    "Thor": Rarity.LEGENDARY,
    "Loki": Rarity.LEGENDARY,
    "Hel": Rarity.LEGENDARY,
    "Njord": Rarity.LEGENDARY,
    "Freya": Rarity.EPIC,
    "Tyr": Rarity.EPIC,
    "Heimdall": Rarity.EPIC,
    "Sif": Rarity.EPIC,
    "Ullr": Rarity.EPIC,
    "Baldr": Rarity.EPIC,
    "Frigg": Rarity.RARE,
    "Skadi": Rarity.RARE,
    "Bragi": Rarity.RARE,
    "Vidar": Rarity.COMMON,
    "Ymir": Rarity.COMMON,
}


class Command(BaseCommand):
    """Seed synergy tags and rebalance rarities."""

    help = "Assigns synergy tags and rebalances rarities for all gods"

    def handle(self, *args, **options):
        self.stdout.write("Rebalancing god rarities...")
        updated = 0
        for name, rarity in RARITY_REBALANCE.items():
            count = God.objects.filter(name=name).update(rarity=rarity)
            if count:
                updated += 1
        self.stdout.write(self.style.SUCCESS(f"Updated {updated} god rarities"))

        self.stdout.write("Seeding synergy tags...")
        GodSynergyTag.objects.all().delete()
        tags_created = 0
        for name, tags in SYNERGY_TAGS_DATA.items():
            try:
                god = God.objects.get(name=name)
            except God.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"  God '{name}' not found, skipping")
                )
                continue
            for tag in tags:
                GodSynergyTag.objects.get_or_create(god=god, tag=tag)
                tags_created += 1
        self.stdout.write(
            self.style.SUCCESS(
                f"Created {tags_created} synergy tags"
                f" for {len(SYNERGY_TAGS_DATA)} gods"
            )
        )
