# Generated by Django 5.1.1 on 2024-10-26 04:34

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payment", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="shippingaddress",
            name="phone",
            field=models.CharField(
                blank=True,
                max_length=10,
                validators=[
                    django.core.validators.RegexValidator(
                        message="Phone number must be exactly 10 digits.",
                        regex="^\\d{10}$",
                    )
                ],
            ),
        ),
    ]
