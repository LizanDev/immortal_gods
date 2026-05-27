"""Teams admin configuration."""

from django.contrib import admin

from .models import Team, TeamMember


class TeamMemberInline(admin.TabularInline):
    """Inline admin for team members."""

    model = TeamMember
    extra = 1


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """Admin interface for Team model."""

    list_display = ("name", "player", "created_at")
    list_filter = ("player",)
    search_fields = ("name",)
    inlines = [TeamMemberInline]


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    """Admin interface for TeamMember model."""

    list_display = ("team", "god", "position")
    list_filter = ("position",)
