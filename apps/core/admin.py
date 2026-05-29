"""Core admin configuration."""

import secrets
import string

from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .models import GiftNotification, PlayerProfile, ReferralCode


@admin.register(PlayerProfile)
class PlayerProfileAdmin(admin.ModelAdmin):
    """Admin interface for PlayerProfile model."""

    list_display = ("user", "gems", "gold", "campaign_progress")
    search_fields = ("user__username",)
    actions = ["send_gems"]

    def send_gems(self, request, queryset):
        """Redirect to a custom form to send gems."""
        if "apply" in request.POST:
            gems = int(request.POST.get("gems", 1000))
            gold = int(request.POST.get("gold", 0))
            message_text = request.POST.get(
                "message", "¡Has recibido un regalo del administrador!"
            )
            count = 0
            for profile in queryset:
                GiftNotification.objects.create(
                    player=profile, gems=gems, gold=gold, message=message_text
                )
                profile.add_gems(gems)
                profile.add_gold(gold)
                count += 1
            self.message_user(
                request,
                f"✅ {count} notificaciones enviadas: {gems}💎 + {gold}🥇",
            )
            return HttpResponseRedirect(request.get_full_path())

        return render(
            request,
            "admin/send_gems.html",
            {
                "players": queryset,
                "action": "send_gems",
                "action_checkbox_name": admin.ACTION_CHECKBOX_NAME,
                "opts": self.model._meta,
            },
        )

    send_gems.short_description = "🎁 Enviar gemas/oro a jugadores seleccionados"


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
            ReferralCode.objects.get_or_create(
                code=code, defaults={"gems_reward": 4000}
            )
            created += 1
        self.message_user(request, f"Generated {created} new referral codes.")

    generate_codes.short_description = "Generate 10 random referral codes"


@admin.register(GiftNotification)
class GiftNotificationAdmin(admin.ModelAdmin):
    """Admin interface for GiftNotification model."""

    list_display = ("player", "gems", "gold", "message", "seen", "created_at")
    list_filter = ("seen", "created_at")
    search_fields = ("player__user__username", "message")
    readonly_fields = ("seen",)
