from django.db import migrations


def remove_zodiac_ladder(apps, schema_editor):
    """Remove orphaned Zodiac faction ladder from production."""
    FactionLadder = apps.get_model("campaign", "FactionLadder")
    FactionLadder.objects.filter(pantheon="zodiac").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("campaign", "0005_campaignbattle_log_json"),
    ]

    operations = [
        migrations.RunPython(remove_zodiac_ladder, migrations.RunPython.noop),
    ]
