"""Core admin configuration."""

import secrets
import string

from django.contrib import admin

from .models import PlayerProfile, ReferralCode


@admin.register(PlayerProfile)
class PlayerProfileAdmin(admin.ModelAdmin):
    """Admin interface for PlayerProfile model."""

    list_display = ("user", "gems", "gold", "energy", "campaign_progress")
    search_fields = ("user__username",)


@admin.register(ReferralCode)
class ReferralCodeAdmin(admin.ModelAdmin):
    """Admin interface for ReferralCode model."""

    list_display = ("code", "gems_reward", "used_by", "used_at", "created_at")
    list_filter = ("used_by", "created_at")
    search_fields = ("code", "used_by__username")
    readonly_fields = ("used_at",)
    actions = ["generate_codes"]

    def generate_codes(self, request, queryset):
        """Generate new referral codes."""
        chars = string.ascii_uppercase + string.digits
        count = 10
        created = 0
        for _ in range(count):
            code = "".join(secrets.choice(chars) for _ in range(8))
            ReferralCode.objects.get_or_create(code=code, defaults={"gems_reward": 4000})
            created += 1
        self.message_user(request, f"Generated {created} new referral codes.")

    generate_codes.short_description = "Generate 10 random referral codes"
