# Generated by Django 5.1.2 on 2024-10-20 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Home", "0005_rename_product_discount_price_product_product_marked_price"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="product_marked_price",
            field=models.DecimalField(
                blank=True, decimal_places=2, default=0, max_digits=8, null=True
            ),
        ),
    ]
