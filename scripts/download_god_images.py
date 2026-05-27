import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

import urllib.request
from apps.gods.models import God

media_dir = "media/gods"
os.makedirs(media_dir, exist_ok=True)

gods = God.objects.all()
saved = 0
errors = 0

for god in gods:
    filename = god.name.lower().replace(" ", "_") + ".jpg"
    filepath = os.path.join(media_dir, filename)

    if os.path.exists(filepath):
        print(f"  {god.name}: already exists")
        saved += 1
        continue

    url = god.image_url
    try:
        print(f"  Downloading {god.name}...")
        urllib.request.urlretrieve(url, filepath)
        god.image = "gods/" + filename
        god.save(update_fields=["image"])
        saved += 1
    except Exception as e:
        print(f"  ERROR {god.name}: {e}")
        errors += 1

print(f"Done. Saved: {saved}, Errors: {errors}")
