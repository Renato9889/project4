# Generated by Django 4.2.2 on 2023-11-23 15:08

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("network", "0017_profile_is_editable"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="profile",
            name="is_editable",
        ),
    ]
