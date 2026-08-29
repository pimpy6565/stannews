from django.contrib import admin
from .models import chats, Story

# Register your models here.
admin.site.register(chats)


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ("title", "kicker", "accent", "is_published", "published_at")
    list_filter = ("is_published", "accent")
    search_fields = ("title", "kicker")
    date_hierarchy = "published_at"
    ordering = ("-published_at",)
