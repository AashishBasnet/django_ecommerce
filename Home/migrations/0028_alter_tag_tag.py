# Generated by Django 5.1.3 on 2024-11-25 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Home", "0027_alter_product_product_rating"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tag",
            name="tag",
            field=models.CharField(max_length=10, unique=True),
        ),
    ]
