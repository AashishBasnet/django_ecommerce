# Generated by Django 5.1.3 on 2024-11-30 06:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0003_alter_post_content"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="post",
            name="is_published",
        ),
    ]
