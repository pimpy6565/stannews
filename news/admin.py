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
    list_display = ("username", "is_active", "is_free", "paid_until")
    list_filter = ("is_active", "is_free")
    search_fields = ("username",)
    list_editable = ("is_free", "is_active")
    actions = ["mark_zelle_received"]

    @admin.action(description="Mark Zelle received (30 days)")
    def mark_zelle_received(self, request, queryset):
        now = timezone.now()
        for row in queryset:
            if row.is_free:
                row.is_active = True
                row.save(update_fields=["is_active"])
                continue
            start = row.paid_until if row.paid_until and row.paid_until > now else now
            row.paid_until = start + timedelta(days=30)
            row.is_active = True
            row.save(update_fields=["paid_until", "is_active"])
