# Generated by Django 5.1.4 on 2025-01-05 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payment", "0011_order_invoice_order_paid"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="is_via_esewa",
            field=models.BooleanField(default=False),
        ),
    ]
