# Generated by Django 5.2 on 2025-04-15 18:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("app_scinet", "0003_alter_interaction_type"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Interaction",
        ),
    ]
