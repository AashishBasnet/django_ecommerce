# Generated by Django 5.1.4 on 2024-12-20 11:07

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Home", "0041_bannerimage"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserReview",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("username", models.CharField(max_length=100)),
                ("review", models.TextField()),
                (
                    "rating",
                    models.DecimalField(
                        decimal_places=1,
                        max_digits=3,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(0.0),
                            django.core.validators.MaxValueValidator(5.0),
                        ],
                    ),
                ),
                ("is_useful", models.BooleanField(default=False)),
                ("review_date", models.DateField(default=datetime.date.today)),
            ],
        ),
    ]
