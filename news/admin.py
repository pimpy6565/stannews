from django.contrib import admin
from django.utils import timezone
from datetime import timedelta
from .models import chats, Story, UsernameSub

admin.site.register(chats)


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ("title", "kicker", "accent", "is_published", "published_at")
    list_filter = ("is_published", "accent")
    search_fields = ("title", "kicker")
    date_hierarchy = "published_at"
    ordering = ("-published_at",)


@admin.register(UsernameSub)
class UsernameSubAdmin(admin.ModelAdmin):
    list_display = ("username", "access_tier", "is_active", "is_free", "paid_until")
    list_filter = ("access_tier", "is_active", "is_free")
    search_fields = ("username",)
    list_editable = ("access_tier", "is_free", "is_active")
    actions = ["mark_zelle_received"]

    @admin.action(description="Mark Zelle received (30 days)")
    def mark_zelle_received(self, request, queryset):
        now = timezone.now()
        for row in queryset:
            if row.is_free:
                row.is_active = True
                if row.access_tier == UsernameSub.ACCESS_NO:
                    row.access_tier = UsernameSub.ACCESS_FULL
                    row.save(update_fields=["is_active", "access_tier"])
                else:
                    row.save(update_fields=["is_active"])
                continue
            start = row.paid_until if row.paid_until and row.paid_until > now else now
            row.paid_until = start + timedelta(days=30)
            row.is_active = True
            fields = ["paid_until", "is_active"]
            if row.access_tier == UsernameSub.ACCESS_NO:
                row.access_tier = UsernameSub.ACCESS_FULL
                fields.append("access_tier")
            row.save(update_fields=fields)
