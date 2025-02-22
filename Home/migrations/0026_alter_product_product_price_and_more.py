# Generated by Django 5.1.3 on 2024-11-23 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Home", "0025_alter_product_product_long_description"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="product_price",
            field=models.DecimalField(decimal_places=2, max_digits=8),
        ),
        migrations.AlterField(
            model_name="product",
            name="product_sale_price",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=8, null=True
            ),
        ),
    ]
