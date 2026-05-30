"""Grant the best possible 5-god team to a player."""
from collections import defaultdict
from itertools import combinations

from django.core.management.base import BaseCommand

from apps.core.models import PlayerProfile
from apps.gods.models import (
    CLASS_ADVANTAGE_BONUS,
    CLASS_ADVANTAGES,
    SYNERGY_BONUSES,
    ULTRA_BUFF_POWER_SURGE,
    God,
    PlayerGod,
)
from apps.teams.models import Team, TeamMember


def find_best_team() -> tuple[list, dict]:
    """Exhaustively search all 5-god combos for the best final power."""
    all_gods = list(God.objects.all().prefetch_related("synergy_tags"))
    thresholds = sorted(SYNERGY_BONUSES.keys(), reverse=True)

    god_data = []
    for god in all_gods:
        tags = list(god.synergy_tags.values_list("tag", flat=True))
        power = (god.base_attack + 10) + (god.base_defense + 5)
        god_data.append({"god": god, "name": god.name, "role": god.role, "power": power, "tags": tags})

    best_score = 0
    best_combo = None
    best_stats = None

    for combo in combinations(god_data, 5):
        base = sum(g["power"] for g in combo)

        role_counts = defaultdict(int)
        for g in combo:
            role_counts[g["role"]] += 1
        class_bonus = 0.0
        for role, cnt in role_counts.items():
            countered = CLASS_ADVANTAGES.get(role)
            if countered and countered in role_counts:
                class_bonus += cnt * CLASS_ADVANTAGE_BONUS
        class_mult = 1.0 + min(class_bonus, 0.5)

        tag_counts = defaultdict(int)
        for g in combo:
            for t in g["tags"]:
                tag_counts[t] += 1
        active_tags = {t: c for t, c in tag_counts.items() if c >= 2}
        max_bonus = 0.0
        for cnt in active_tags.values():
            for th in thresholds:
                if cnt >= th:
                    max_bonus = max(max_bonus, SYNERGY_BONUSES[th]["stat_bonus_pct"])
                    break
        if any(c >= 5 for c in active_tags.values()):
            max_bonus += ULTRA_BUFF_POWER_SURGE
        synergy_mult = 1.0 + max_bonus
        final = int(base * class_mult * synergy_mult)

        if final > best_score:
            best_score = final
            best_combo = combo
            best_stats = {
                "base": base,
                "class_mult": class_mult,
                "synergy_mult": synergy_mult,
                "active_tags": active_tags,
                "final": final,
            }

    return best_combo, best_stats


class Command(BaseCommand):
    """Grant the best possible 5-god team to a player."""

    help = "Grants the optimal 5-god team (wisdom x5 ultra_buff) to a player"

    def add_arguments(self, parser):
        parser.add_argument("username", type=str, help="Player's username")

    def handle(self, *args, **options):
        username = options["username"]
        profile = PlayerProfile.objects.select_related("user").get(user__username=username)
        self.stdout.write(f"Player: {profile.user.username} (id={profile.id})")

        self.stdout.write("Searching best team from all gods...")
        best_combo, stats = find_best_team()

        self.stdout.write(f"\nBest team found — Final Power: {stats['final']}")
        self.stdout.write(f"  Base: {stats['base']} | Class: {stats['class_mult']:.2f} | Synergy: {stats['synergy_mult']:.2f}")
        self.stdout.write(f"  Ultra buff: {any(c >= 5 for c in stats['active_tags'].values())}")
        self.stdout.write(f"  Active tags: {stats['active_tags']}")

        team_name = "Legión Suprema"
        Team.objects.filter(player=profile, name=team_name).delete()

        player_gods = []
        for gd in best_combo:
            existing = PlayerGod.objects.filter(player=profile, god=gd["god"]).first()
            if existing:
                self.stdout.write(f"  {gd['name']:20s} → already owned (lv.{existing.level})")
                player_gods.append(existing)
            else:
                pg = PlayerGod.objects.create(
                    player=profile,
                    god=gd["god"],
                    level=20,
                    quality_tier=4,
                )
                self.stdout.write(f"  {gd['name']:20s} → CREATED (lv.20, epic)")
                player_gods.append(pg)

        team = Team.objects.create(player=profile, name=team_name)
        for i, pg in enumerate(player_gods, 1):
            TeamMember.objects.create(team=team, god=pg, position=i)

        team_power = sum(pg.total_attack + pg.total_defense for pg in player_gods)
        self.stdout.write(self.style.SUCCESS(
            f"\nTeam '{team_name}' ready — {len(player_gods)} gods, power={int(team_power * team.get_class_advantage_multiplier() * team.get_synergy_multiplier())}"
        ))
        for s in team.get_synergy_details():
            ultra = " + ULTRA BUFF" if s["count"] >= 5 else ""
            self.stdout.write(f"  {s['tag']} x{s['count']} = +{s['bonus_pct_display']}%{ultra}")
