# Generated by Django 5.1.2 on 2024-10-21 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Home", "0009_alter_product_product_category"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="product_slug",
            field=models.SlugField(blank=True, null=True, unique=True),
        ),
    ]
