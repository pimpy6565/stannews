from django.db import models

# Create your models here.
class chats(models.Model):
    text = models.TextField()
        
    def __str__(self):
        return self.text     


class Story(models.Model):
    ACCENT_AMBER = "amber"
    ACCENT_PR = "pr"
    ACCENT_LIGHT = "light"
    ACCENT_CHOICES = [
        (ACCENT_AMBER, "Amber (default news card)"),
        (ACCENT_PR, "Puerto Rican red/blue"),
        (ACCENT_LIGHT, "Light (legacy)"),
    ]
    title = models.CharField(max_length=220)
    kicker = models.CharField(max_length=80, blank=True, help_text="Pill text, e.g. LOCAL • AUGUST 28, 2026")
    dek = models.TextField(blank=True, help_text="Subtitle under the headline")
    body = models.TextField(help_text="HTML below the dek. YouTube, galleries, Stan Tips ok.")
    hero_image_url = models.CharField(max_length=500, blank=True, help_text="Full http(s) URL or static path like news/pr_parade_hero.jpg")
    hero_caption = models.CharField(max_length=300, blank=True)
    accent = models.CharField(max_length=20, choices=ACCENT_CHOICES, default=ACCENT_AMBER)
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-published_at"]

    def __str__(self):
        return self.title
