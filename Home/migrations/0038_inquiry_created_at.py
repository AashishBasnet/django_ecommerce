# Generated by Django 5.1.4 on 2024-12-11 10:47

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Home", "0037_alter_product_product_description"),
    ]

    operations = [
        migrations.AddField(
            model_name="inquiry",
            name="created_at",
            field=models.DateField(default=datetime.date.today),
        ),
    ]
