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


class UsernameSub(models.Model):
    ACCESS_NO = "no_access"
    ACCESS_PHONE = "phone"
    ACCESS_COMPUTER = "computer"
    ACCESS_FULL = "full_lab_ops"
    ACCESS_CHOICES = [
        (ACCESS_NO, "No access"),
        (ACCESS_PHONE, "Phone"),
        (ACCESS_COMPUTER, "Computer"),
        (ACCESS_FULL, "Full Lab Ops"),
    ]
    username = models.CharField(max_length=150, unique=True)
    is_active = models.BooleanField(default=False)
    is_free = models.BooleanField(default=False, help_text="Complimentary: skip Zelle.")
    paid_until = models.DateTimeField(null=True, blank=True)
    access_tier = models.CharField(
        max_length=20,
        choices=ACCESS_CHOICES,
        default=ACCESS_NO,
        help_text="Lab Ops device gate: no_access / phone / computer / full_lab_ops.",
    )

    def __str__(self):
        return self.username

    def is_paid_or_free(self):
        """Lab Ops paid gate: only admin Active or Free. paid_until alone is not enough."""
        return bool(self.is_free) or bool(self.is_active)

    def allows_device(self, is_phone: bool) -> bool:
        if self.access_tier == self.ACCESS_NO:
            return False
        if self.access_tier == self.ACCESS_FULL:
            return True
        if self.access_tier == self.ACCESS_PHONE:
            return bool(is_phone)
        if self.access_tier == self.ACCESS_COMPUTER:
            return not bool(is_phone)
        return False
