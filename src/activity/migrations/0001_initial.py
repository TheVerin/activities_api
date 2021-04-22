# Generated by Django 3.2 on 2021-04-22 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Activity",
            fields=[
                (
                    "id",
                    models.CharField(
                        editable=False,
                        max_length=20,
                        unique=True,
                        serialize=True,
                        primary_key=True,
                    ),
                ),
                ("activity_date", models.DateTimeField()),
                ("track_id", models.CharField(max_length=10)),
                (
                    "status",
                    models.CharField(
                        blank=True,
                        choices=[("A", "A"), ("S", "S"), ("R", "R")],
                        max_length=1,
                    ),
                ),
                ("billig_amount", models.DecimalField(decimal_places=2, max_digits=8)),
            ],
        ),
    ]
