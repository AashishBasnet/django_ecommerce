from django import forms
from .models import ShippingAddress
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


class ShippingForm(forms.ModelForm):
    shipping_full_name = forms.CharField(max_length=255, required=True, label="",
                                         widget=forms.TextInput(
                                             attrs={'class': 'form-control', 'placeholder': 'Fullname'}))
    shipping_address1 = forms.CharField(max_length=255, required=True, label="",
                                        widget=forms.TextInput(
                                            attrs={'class': 'form-control', 'placeholder': 'Address Line 1'}))
    shipping_address2 = forms.CharField(max_length=255, required=False, label="",
                                        widget=forms.TextInput(
                                            attrs={'class': 'form-control', 'placeholder': 'Address Line 2'}))
    shipping_city = forms.CharField(max_length=255, required=True, label="",
                                    widget=forms.TextInput(
                                        attrs={'class': 'form-control', 'placeholder': 'City'}))
    shipping_state = forms.CharField(max_length=255, required=False, label="",
                                     widget=forms.TextInput(
                                         attrs={'class': 'form-control', 'placeholder': 'State'}))
    shipping_zipcode = forms.CharField(max_length=255, required=False, label="",
                                       widget=forms.TextInput(
                                           attrs={'class': 'form-control', 'placeholder': 'Zip Code'}))
    shipping_country = forms.CharField(max_length=255, required=True, label="",
                                       widget=forms.TextInput(
                                           attrs={'class': 'form-control', 'placeholder': 'Country'}))
    shipping_email = forms.EmailField(max_length=255, required=False, label="",
                                      widget=forms.TextInput(
                                          attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    shipping_phone = forms.CharField(max_length=10, required=False, label="",
                                     widget=forms.TextInput(
                                         attrs={'class': 'form-control', 'placeholder': 'Phone Number'}), validators=[
                                         RegexValidator(
                                             regex=r'^\d{10}$',
                                             message="Phone number must be exactly 10 digits."
                                         )])

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('shipping_email')
        phone = cleaned_data.get('shipping_phone')

        if not email and not phone:
            raise ValidationError(
                "Either email or phone number must be provided.")

        return cleaned_data

    class Meta:
        model = ShippingAddress
        fields = ['shipping_full_name', 'shipping_email', 'shipping_address1', 'shipping_address2',
                  'shipping_city', 'shipping_state', 'shipping_zipcode', 'shipping_country', 'shipping_phone']
        exclude = ['user',]
