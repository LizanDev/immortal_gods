"""Teams models."""

from collections import defaultdict

from django.db import models

from apps.gods.models import (
    CLASS_ADVANTAGE_BONUS,
    CLASS_ADVANTAGES,
    SYNERGY_BONUSES,
    GodSynergyTag,
)

MAX_TEAM_SIZE = 5


class Team(models.Model):
    """Represents a team of up to 5 gods."""

    player = models.ForeignKey(
        "core.PlayerProfile", on_delete=models.CASCADE, related_name="teams"
    )
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name

    def god_count(self) -> int:
        """Return the number of gods in the team."""
        return self.members.count()

    def is_full(self) -> bool:
        """Check if the team has reached maximum size."""
        return self.god_count() >= MAX_TEAM_SIZE

    def get_class_advantage_multiplier(self) -> float:
        """Calculate class advantage bonus for battle power."""
        if self.god_count() == 0:
            return 1.0

        role_counts: dict[str, int] = {}
        for member in self.members.select_related("god__god").all():
            if member.god and member.god.god:
                role = member.god.god.role
                role_counts[role] = role_counts.get(role, 0) + 1

        bonus = 0.0
        for role, count in role_counts.items():
            countered_role = CLASS_ADVANTAGES.get(role)
            if countered_role and countered_role in role_counts:
                bonus += count * CLASS_ADVANTAGE_BONUS

        return 1.0 + min(bonus, 0.5)

    def get_synergy_tags_active(self) -> dict[str, int]:
        """Count how many gods share each synergy tag."""
        if self.god_count() == 0:
            return {}

        god_ids = [
            m.god.god_id
            for m in self.members.select_related("god").all()
            if m.god
        ]
        tag_counts: dict[str, int] = defaultdict(int)
        for tag in GodSynergyTag.objects.filter(
            god_id__in=god_ids
        ).values_list("tag", flat=True):
            tag_counts[tag] += 1
        return {tag: count for tag, count in tag_counts.items() if count >= 2}

    def get_synergy_bonus_pct(self) -> float:
        """Calculate total stat bonus from active synergies."""
        tag_counts = self.get_synergy_tags_active()
        if not tag_counts:
            return 0.0

        max_bonus = 0.0
        thresholds = sorted(SYNERGY_BONUSES.keys(), reverse=True)
        for count in tag_counts.values():
            for threshold in thresholds:
                if count >= threshold:
                    max_bonus = max(
                        max_bonus, SYNERGY_BONUSES[threshold]["stat_bonus_pct"]
                    )
                    break
        return max_bonus

    def get_synergy_multiplier(self) -> float:
        """Get combined multiplier from synergy bonuses."""
        return 1.0 + self.get_synergy_bonus_pct()

    def get_synergy_details(self) -> list[dict]:
        """Return list of active synergies with details."""
        tag_counts = self.get_synergy_tags_active()
        if not tag_counts:
            return []

        details = []
        for tag, count in sorted(tag_counts.items()):
            thresholds = sorted(SYNERGY_BONUSES.keys(), reverse=True)
            for threshold in thresholds:
                if count >= threshold:
                    bonus = SYNERGY_BONUSES[threshold]["stat_bonus_pct"]
                    detail = {
                        "tag": tag,
                        "count": count,
                        "threshold": threshold,
                        "bonus_pct": bonus,
                    }
                    details.append(detail)
                    break
        return details


class TeamMember(models.Model):
    """Represents a god assigned to a team."""

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="members")
    god = models.ForeignKey("gods.PlayerGod", on_delete=models.CASCADE)
    position = models.PositiveIntegerField(
        choices=[(i, f"Position {i}") for i in range(1, MAX_TEAM_SIZE + 1)]
    )

    class Meta:
        unique_together = ["team", "position"]
        ordering = ["position"]

    def __str__(self) -> str:
        return f"{self.god.god.name} in {self.team.name}"
