from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


class ShippingAddress(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    shipping_full_name = models.CharField(max_length=255)
    shipping_address1 = models.CharField(max_length=255)
    shipping_address2 = models.CharField(max_length=255, null=True, blank=True)
    shipping_city = models.CharField(max_length=255)
    shipping_state = models.CharField(max_length=255, null=True, blank=True)
    shipping_zipcode = models.CharField(max_length=255, null=True, blank=True)
    shipping_country = models.CharField(max_length=255)
    shipping_email = models.EmailField(max_length=255, null=True, blank=True)
    shipping_phone = models.CharField(max_length=10, null=True, blank=True, validators=[
        RegexValidator(
            regex=r'^\d{10}$',
            message="Phone number must be exactly 10 digits."
        )])

    def clean(self):
        super().clean()
        if not self.shipping_email and not self.shipping_phone:
            raise ValidationError(
                "Either email or phone number must be provided.")

    class Meta:
        verbose_name_plural = "Shipping Address"

    def __str__(self):
        return f'Shipping Address - {str(self.id)}'
