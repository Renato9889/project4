# Generated by Django 4.2.2 on 2023-11-23 14:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("network", "0014_follow_user_following"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="is_editing",
            field=models.BooleanField(default=False),
        ),
    ]
