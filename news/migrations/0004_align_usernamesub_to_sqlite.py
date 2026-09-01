from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("news", "0003_usernamesub"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(model_name="usernamesub", name="last_marked_at"),
                migrations.RemoveField(model_name="usernamesub", name="note"),
                migrations.AddField(
                    model_name="usernamesub",
                    name="is_active",
                    field=models.BooleanField(default=False),
                ),
            ],
            database_operations=[
                # Live SQLite already has is_active and does not have last_marked_at/note.
            ],
        ),
    ]
