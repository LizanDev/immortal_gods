"""Check which items exist in the database."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.items.models import Item
from apps.core.management.commands.seed_data import ITEMS_DATA

print(f"Items currently in DB: {Item.objects.filter(belongs_to_god__isnull=False).exclude(belongs_to_god='').count()}")
print("\nItems that will be created:")
for item in ITEMS_DATA:
    exists = Item.objects.filter(name=item['name']).exists()
    status = "[EXISTS]" if exists else "[NEW]"
    god = item.get('belongs_to_god', 'none')
    print(f"  {status} {item['name']} ({god})")
