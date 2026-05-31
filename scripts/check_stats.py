"""Verify stat ranges match new rarities."""
import os; os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'; os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'
import django; django.setup()
from apps.gods.models import God

RANGES = {
    "common":     {"atk": (90, 120),   "def": (75, 105)},
    "rare":       {"atk": (125, 155),  "def": (110, 140)},
    "epic":       {"atk": (160, 195),  "def": (140, 175)},
    "legendary":  {"atk": (205, 250),  "def": (185, 225)},
    "mythic":     {"atk": (260, 330),  "def": (235, 300)},
}

errors = []
for god in God.objects.all().order_by("pantheon", "name"):
    r = RANGES[god.rarity]
    atk_ok = r["atk"][0] <= god.base_attack <= r["atk"][1]
    def_ok = r["def"][0] <= god.base_defense <= r["def"][1]
    if not atk_ok:
        errors.append(f"{god.name:25s} {god.rarity:12s} ATK={god.base_attack:4d} (range {r['atk'][0]}-{r['atk'][1]})")
    if not def_ok:
        errors.append(f"{god.name:25s} {god.rarity:12s} DEF={god.base_defense:4d} (range {r['def'][0]}-{r['def'][1]})")

if errors:
    print("ERRORS:")
    for e in errors:
        print(f"  {e}")
else:
    print("All 78 gods have stats within their rarity range ✓")

# Show a few examples
print("\nExamples:")
for god in God.objects.filter(name__in=["Hades", "Poseidon", "Hephaestus", "Osiris", "Bastet", "Thor", "Coatlicue"]):
    print(f"  {god.name:20s} {god.rarity:12s} ATK={god.base_attack:4d} DEF={god.base_defense:4d}")
