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
    list_display = ("username", "access_ok", "is_free", "paid_until", "last_marked_at")
    list_filter = ("is_free",)
    search_fields = ("username",)
    list_editable = ("is_free",)
    actions = ["mark_zelle_received"]

    @admin.display(boolean=True, description="Access OK")
    def access_ok(self, obj):
        return obj.is_active()

    @admin.action(description="Mark Zelle received (30 days)")
    def mark_zelle_received(self, request, queryset):
        now = timezone.now()
        for row in queryset:
            if row.is_free:
                row.last_marked_at = now
                row.save(update_fields=["last_marked_at"])
                continue
            start = row.paid_until if row.paid_until and row.paid_until > now else now
            row.paid_until = start + timedelta(days=30)
            row.last_marked_at = now
            row.save(update_fields=["paid_until", "last_marked_at"])
