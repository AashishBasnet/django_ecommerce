# Generated by Django 5.1.1 on 2024-10-26 04:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payment", "0003_alter_shippingaddress_email_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="shippingaddress",
            name="address2",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
