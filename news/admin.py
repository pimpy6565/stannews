from django.contrib import admin
from django.utils import timezone
from datetime import timedelta
from .models import chats, Story, UsernameSub

# Register your models here.
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
    list_display = ("username", "is_free", "paid_until", "last_marked_at")
    list_filter = ("is_free",)
    search_fields = ("username",)
    actions = ["mark_zelle_received"]

    @admin.action(description="Mark Zelle $1 received")
    def mark_zelle_received(self, request, queryset):
        now = timezone.now()
        until = now + timedelta(days=30)
        queryset.update(paid_until=until, last_marked_at=now)
