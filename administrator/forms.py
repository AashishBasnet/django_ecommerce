from django import forms
from Home.models import Product, Categories
from tinymce.widgets import TinyMCE


class AddProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = [
            'product_name',
            'product_price',
            'product_category',
            'product_description',
            'product_long_description',
            'product_additional_information',
            'product_image',
            'product_tag',
            'product_rating',
            'product_sale_price',
            'stock',]


class AddCategoryForm(forms.ModelForm):

    class Meta:
        model = Categories
        fields = [
            'category_name',
            'category_display_image',
        ]
