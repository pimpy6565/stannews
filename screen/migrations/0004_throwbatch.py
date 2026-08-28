from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("screen", "0003_hplc_ace_high_hplc_ace_low_hplc_asp_high_and_more"),
    ]
    operations = [
        migrations.CreateModel(
            name="ThrowBatch",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("flavor", models.CharField(max_length=80)),
                ("finished_brix", models.DecimalField(decimal_places=3, max_digits=10)),
                ("syrup_brix", models.DecimalField(decimal_places=3, max_digits=10)),
                ("batch_gallons", models.DecimalField(decimal_places=3, max_digits=12)),
                ("syrup_gallons", models.DecimalField(decimal_places=3, max_digits=12)),
                ("water_gallons", models.DecimalField(decimal_places=3, max_digits=12)),
                ("ran_by", models.CharField(max_length=150)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
