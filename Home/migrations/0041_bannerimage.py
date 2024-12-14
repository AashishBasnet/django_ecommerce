# Generated by Django 5.1.4 on 2024-12-13 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Home", "0040_alter_inquiry_subject"),
    ]

    operations = [
        migrations.CreateModel(
            name="BannerImage",
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
                ("image", models.ImageField(null=True, upload_to="uploads/banners/")),
            ],
        ),
    ]
