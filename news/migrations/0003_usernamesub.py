from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("news", "0002_story"),
    ]

    operations = [
        migrations.CreateModel(
            name="UsernameSub",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("username", models.CharField(max_length=150, unique=True)),
                ("is_free", models.BooleanField(default=False, help_text="Works with no Zelle.")),
                ("paid_until", models.DateTimeField(blank=True, null=True)),
                ("last_marked_at", models.DateTimeField(blank=True, null=True)),
                ("note", models.CharField(blank=True, max_length=200)),
            ],
        ),
    ]
