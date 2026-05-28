import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from collections import Counter

GODS_DATA = [
    # Greek Gods
    {"name": "Zeus", "pantheon": "greek"},
    {"name": "Poseidon", "pantheon": "greek"},
    {"name": "Hades", "pantheon": "greek"},
    {"name": "Ares", "pantheon": "greek"},
    {"name": "Athena", "pantheon": "greek"},
    {"name": "Apollo", "pantheon": "greek"},
    {"name": "Artemis", "pantheon": "greek"},
    {"name": "Hermes", "pantheon": "greek"},
    {"name": "Hephaestus", "pantheon": "greek"},
    {"name": "Demeter", "pantheon": "greek"},
    {"name": "Cronus", "pantheon": "greek"},
    {"name": "Gaia", "pantheon": "greek"},
    {"name": "Prometheus", "pantheon": "greek"},
    {"name": "Hecate", "pantheon": "greek"},
    {"name": "Persephone", "pantheon": "greek"},
    {"name": "Dionysus", "pantheon": "greek"},
    {"name": "Eros", "pantheon": "greek"},
    {"name": "Nike", "pantheon": "greek"},
    {"name": "Morpheus", "pantheon": "greek"},
    # Zodiac Gods
    {"name": "Aries", "pantheon": "zodiac"},
    {"name": "Taurus", "pantheon": "zodiac"},
    {"name": "Gemini", "pantheon": "zodiac"},
    {"name": "Cancer", "pantheon": "zodiac"},
    {"name": "Leo", "pantheon": "zodiac"},
    {"name": "Virgo", "pantheon": "zodiac"},
    {"name": "Libra", "pantheon": "zodiac"},
    {"name": "Scorpio", "pantheon": "zodiac"},
    {"name": "Sagittarius", "pantheon": "zodiac"},
    {"name": "Capricorn", "pantheon": "zodiac"},
    {"name": "Aquarius", "pantheon": "zodiac"},
    {"name": "Pisces", "pantheon": "zodiac"},
    # Chinese Gods
    {"name": "Jade Emperor", "pantheon": "chinese"},
    {"name": "Sun Wukong", "pantheon": "chinese"},
    {"name": "Nezha", "pantheon": "chinese"},
    {"name": "Erlang Shen", "pantheon": "chinese"},
    {"name": "Chang'e", "pantheon": "chinese"},
    {"name": "Dragon King", "pantheon": "chinese"},
    {"name": "Guan Yu", "pantheon": "chinese"},
    {"name": "Nuwa", "pantheon": "chinese"},
    {"name": "Zhong Kui", "pantheon": "chinese"},
    {"name": "Caishen", "pantheon": "chinese"},
    {"name": "Fuxi", "pantheon": "chinese"},
    {"name": "Shennong", "pantheon": "chinese"},
    {"name": "Xiwangmu", "pantheon": "chinese"},
    {"name": "Huangdi", "pantheon": "chinese"},
    {"name": "Lei Gong", "pantheon": "chinese"},
    # Egyptian Gods
    {"name": "Ra", "pantheon": "egyptian"},
    {"name": "Osiris", "pantheon": "egyptian"},
    {"name": "Anubis", "pantheon": "egyptian"},
    {"name": "Horus", "pantheon": "egyptian"},
    {"name": "Isis", "pantheon": "egyptian"},
    {"name": "Set", "pantheon": "egyptian"},
    {"name": "Thoth", "pantheon": "egyptian"},
    {"name": "Sekhmet", "pantheon": "egyptian"},
    {"name": "Bastet", "pantheon": "egyptian"},
    {"name": "Ptah", "pantheon": "egyptian"},
    {"name": "Amun", "pantheon": "egyptian"},
    {"name": "Hathor", "pantheon": "egyptian"},
    {"name": "Khepri", "pantheon": "egyptian"},
    {"name": "Ma'at", "pantheon": "egyptian"},
    {"name": "Sobek", "pantheon": "egyptian"},
    {"name": "Seshat", "pantheon": "egyptian"},
    # Nordic Gods
    {"name": "Odin", "pantheon": "nordic"},
    {"name": "Thor", "pantheon": "nordic"},
    {"name": "Loki", "pantheon": "nordic"},
    {"name": "Freya", "pantheon": "nordic"},
    {"name": "Tyr", "pantheon": "nordic"},
    {"name": "Heimdall", "pantheon": "nordic"},
    {"name": "Frigg", "pantheon": "nordic"},
    {"name": "Baldr", "pantheon": "nordic"},
    {"name": "Skadi", "pantheon": "nordic"},
    {"name": "Vidar", "pantheon": "nordic"},
    {"name": "Ymir", "pantheon": "nordic"},
    {"name": "Hel", "pantheon": "nordic"},
    {"name": "Njord", "pantheon": "nordic"},
    {"name": "Sif", "pantheon": "nordic"},
    {"name": "Ullr", "pantheon": "nordic"},
    {"name": "Bragi", "pantheon": "nordic"},
]

pantheons = [g['pantheon'] for g in GODS_DATA]
counts = Counter(pantheons)

print('Dioses por facción:')
print('=' * 40)
for pantheon, count in sorted(counts.items()):
    names = [g['name'] for g in GODS_DATA if g['pantheon'] == pantheon]
    print(f'\n{pantheon.upper()} ({count} dioses):')
    print(', '.join(names))

print()
print(f'TOTAL: {len(GODS_DATA)} dioses')
