"""Teams views."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.gods.models import PlayerGod
from apps.teams.models import MAX_TEAM_SIZE, Team, TeamMember


@login_required
def team_list(request):
    """List all teams for the player."""
    profile = request.user.profile
    teams = profile.teams.all()
    return render(request, "teams/list.html", {"teams": teams, "profile": profile})


@login_required
def team_detail(request, team_id):
    """Show details for a specific team."""
    team = get_object_or_404(Team, pk=team_id, player=request.user.profile)
    return render(request, "teams/detail.html", {"team": team})


@login_required
def team_create(request):
    """Create a new team."""
    profile = request.user.profile
    if request.method == "POST":
        name = request.POST.get("name", "New Team")
        team = Team.objects.create(player=profile, name=name)
        return redirect("teams:detail", team_id=team.id)
    return render(request, "teams/create.html", {"profile": profile})


@login_required
def team_add_member(request, team_id):
    """Add a god to a team."""
    team = get_object_or_404(Team, pk=team_id, player=request.user.profile)

    if team.is_full():
        return redirect("teams:detail", team_id=team.id)

    if request.method == "POST":
        god_id = request.POST.get("god_id")
        position = int(request.POST.get("position", 1))

        player_god = get_object_or_404(
            PlayerGod, pk=god_id, player=request.user.profile
        )

        if team.members.filter(position=position).exists():
            return redirect("teams:detail", team_id=team.id)

        TeamMember.objects.create(team=team, god=player_god, position=position)

    available_gods = PlayerGod.objects.filter(player=request.user.profile).exclude(
        id__in=team.members.values_list("god_id", flat=True)
    )
    positions = [
        i
        for i in range(1, MAX_TEAM_SIZE + 1)
        if not team.members.filter(position=i).exists()
    ]

    return render(
        request,
        "teams/add_member.html",
        {"team": team, "gods": available_gods, "positions": positions},
    )


@login_required
def team_remove_member(request, team_id, member_id):
    """Remove a god from a team."""
    team = get_object_or_404(Team, pk=team_id, player=request.user.profile)
    member = get_object_or_404(TeamMember, pk=member_id, team=team)
    member.delete()
    return redirect("teams:detail", team_id=team.id)


@login_required
def team_delete(request, team_id):
    """Delete a team."""
    team = get_object_or_404(Team, pk=team_id, player=request.user.profile)
    if request.method == "POST":
        team.delete()
        return redirect("teams:list")
    return render(request, "teams/delete.html", {"team": team})
