# Generated by Django 5.1.3 on 2024-12-08 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Home", "0031_alter_product_product_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="inquiry",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
