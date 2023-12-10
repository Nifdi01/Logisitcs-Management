# Generated by Django 4.2.7 on 2023-12-10 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("logistics", "0004_alter_cargoorder_truck"),
    ]

    operations = [
        migrations.AddField(
            model_name="cargoorder",
            name="status",
            field=models.CharField(
                choices=[
                    ("not started", "Not Started"),
                    ("in progress", "In Progress"),
                    ("completed", "Completed"),
                    ("in queue", "In Queue"),
                ],
                default="not started",
                max_length=20,
            ),
        ),
    ]