"""Teams models."""

from django.db import models

from apps.gods.models import CLASS_ADVANTAGE_BONUS, CLASS_ADVANTAGES

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
