"""Check campaign state - all levels."""
import os; os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'; os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'
import django; django.setup()
from apps.campaign.models import CampaignLevel

for level in CampaignLevel.objects.all().order_by('order'):
    enemies = level.enemy_team_data
    total_enemy_pwr = sum(e['attack']+e['defense'] for e in enemies)
    first = enemies[0]
    pwr = first['attack'] + first['defense']
    print(f"L{level.order:2d} {level.difficulty:6s} req={level.required_power:>5d} teamPWR={total_enemy_pwr:>5d} | {first['name']:20s} ATK={first['attack']:4d} DEF={first['defense']:4d} PWR={pwr:5d}")
