from django.core.management.base import BaseCommand

from apps.gods.models import God

PWR_RANGES = {
    "common": (100, 150),
    "rare": (170, 220),
    "epic": (240, 290),
    "legendary": (310, 360),
    "mythic": (380, 430),
}

HP_RANGES = {
    "common": (700, 900),
    "rare": (950, 1150),
    "epic": (1200, 1400),
    "legendary": (1450, 1650),
    "mythic": (1700, 2000),
}

SPEED_RANGES = {
    "common": (80, 130),
    "rare": (80, 130),
    "epic": (80, 135),
    "legendary": (85, 135),
    "mythic": (85, 140),
}


class Command(BaseCommand):
    help = "Rebalance god base stats so each rarity tier has clear separation."

    def handle(self, *args, **options):
        by_rarity: dict[str, list[God]] = {}
        for g in God.objects.all():
            by_rarity.setdefault(g.rarity, []).append(g)

        changed = 0
        for rarity, gods in by_rarity.items():
            pwr_min, pwr_max = PWR_RANGES[rarity]
            hp_min, hp_max = HP_RANGES[rarity]
            spd_min, spd_max = SPEED_RANGES[rarity]

            current = []
            for g in gods:
                current.append({
                    "god": g,
                    "pwr": g.base_attack + g.base_defense,
                    "hp": g.base_hp,
                    "spd": g.base_speed,
                })

            cur_pwr_vals = [c["pwr"] for c in current]
            pwr_range = max(max(cur_pwr_vals) - min(cur_pwr_vals), 1)
            pwr_min_cur = min(cur_pwr_vals)

            cur_hp_vals = [c["hp"] for c in current]
            hp_range = max(max(cur_hp_vals) - min(cur_hp_vals), 1)
            hp_min_cur = min(cur_hp_vals)

            cur_spd_vals = [c["spd"] for c in current]
            spd_range = max(max(cur_spd_vals) - min(cur_spd_vals), 1)
            spd_min_cur = min(cur_spd_vals)

            for c in current:
                g = c["god"]
                old_atk = g.base_attack
                old_def = g.base_defense
                old_hp = g.base_hp
                old_spd = g.base_speed
                old_pwr = c["pwr"]

                pct = (c["pwr"] - pwr_min_cur) / pwr_range
                new_pwr = round(pwr_min + pct * (pwr_max - pwr_min))

                atk_share = old_atk / max(old_pwr, 1)
                new_atk = max(1, round(new_pwr * atk_share))
                new_def = max(1, new_pwr - new_atk)

                pct_hp = (c["hp"] - hp_min_cur) / hp_range
                new_hp = round(hp_min + pct_hp * (hp_max - hp_min))

                pct_spd = (c["spd"] - spd_min_cur) / spd_range
                new_spd = round(spd_min + pct_spd * (spd_max - spd_min))

                g.base_attack = new_atk
                g.base_defense = new_def
                g.base_hp = new_hp
                g.base_speed = new_spd
                g.save()
                changed += 1

                self.stdout.write(
                    f"  {rarity:>10s} {g.name:20s}"
                    f" PWR {old_pwr:3d}->{new_pwr:3d}"
                    f" (ATK {old_atk:3d}->{new_atk:3d} DEF {old_def:3d}->{new_def:3d})"
                    f" HP {old_hp:4d}->{new_hp:4d}"
                    f" SPD {old_spd:3d}->{new_spd:3d}"
                )

        self.stdout.write(self.style.SUCCESS(f"Rebalanced {changed} gods."))
