# Generated by Django 5.1.4 on 2024-12-11 04:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Home", "0033_remove_inquiry_created_at_inquiry_is_reviewed"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="product_description",
            field=models.CharField(blank=True, default="", max_length=300, null=True),
        ),
    ]
