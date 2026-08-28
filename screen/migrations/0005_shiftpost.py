from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("screen", "0004_throwbatch"),
    ]
    operations = [
        migrations.CreateModel(
            name="ShiftPost",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("body", models.CharField(max_length=280)),
                ("posted_by", models.CharField(max_length=150)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
