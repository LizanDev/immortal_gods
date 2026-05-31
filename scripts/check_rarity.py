"""Check rarity distribution per pantheon."""
import os; os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'; os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'
import django; django.setup()
from collections import Counter

from apps.gods.models import God

total = God.objects.count()
print(f"Total gods: {total}\n")

c = Counter(God.objects.values_list("rarity", flat=True))
for r, n in sorted(c.items()):
    print(f"  {r:12s}: {n:2d} ({n*100//total:2d}%)")

pantheons = God.objects.values_list("pantheon", flat=True).distinct().order_by("pantheon")
print()
for p in pantheons:
    qs = God.objects.filter(pantheon=p)
    n = qs.count()
    c2 = Counter(qs.values_list("rarity", flat=True))
    parts = [f"{r}:{c2.get(r,0)}" for r in ["common","rare","epic","legendary","mythic"]]
    print(f"{p:12s} ({n:2d}):  {'  '.join(parts)}")
