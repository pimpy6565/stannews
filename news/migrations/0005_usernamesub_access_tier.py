from django.db import migrations, models
from django.utils import timezone


def forwards_set_tiers(apps, schema_editor):
    UsernameSub = apps.get_model("news", "UsernameSub")
    now = timezone.now()
    for row in UsernameSub.objects.all():
        paid = bool(row.is_free) or bool(row.is_active)
        if row.paid_until is not None and row.paid_until > now:
            paid = True
        row.access_tier = "full_lab_ops" if paid else "no_access"
        row.save(update_fields=["access_tier"])


def backwards_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("news", "0004_align_usernamesub_to_sqlite"),
    ]

    operations = [
        migrations.AddField(
            model_name="usernamesub",
            name="access_tier",
            field=models.CharField(
                choices=[
                    ("no_access", "No access"),
                    ("phone", "Phone"),
                    ("computer", "Computer"),
                    ("full_lab_ops", "Full Lab Ops"),
                ],
                default="no_access",
                help_text="Lab Ops device gate: no_access / phone / computer / full_lab_ops.",
                max_length=20,
            ),
        ),
        migrations.RunPython(forwards_set_tiers, backwards_noop),
    ]
