# Generated by Django 5.1.4 on 2025-01-26 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Home", "0050_alter_product_product_additional_information_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="product_name",
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
