from django import forms
from django.core.exceptions import ValidationError
from Home.models import Product, Categories, Tag
from tinymce.widgets import TinyMCE
from blog.models import Post, Category, Tag as T


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
            'product_rating',
            'product_tag',
            'product_sale_price',
            'stock',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product_tag'].queryset = Tag.objects.exclude(tag__in=[
                                                                  'New', 'Sale'])

    def clean_product_name(self):
        product_name = self.cleaned_data['product_name'].strip()
        normalized_name = product_name.lower()

        if Product.objects.filter(product_name__iexact=product_name).exists():
            raise ValidationError(f"A product with the name '{
                                  product_name}' already exists.")

        # Automatically normalize the name to lowercase to avoid slug conflicts
        self.cleaned_data['product_name'] = normalized_name
        return normalized_name


class AddCategoryForm(forms.ModelForm):
    class Meta:
        model = Categories
        fields = [
            'category_name',
            'category_display_image',
        ]

    def clean_category_name(self):
        category_name = self.cleaned_data['category_name'].strip()
        normalized_name = category_name.lower()

        if Categories.objects.filter(category_name__iexact=category_name).exists():
            raise ValidationError(f"A category with the name '{
                                  category_name}' already exists.")

        # Normalize the name to lowercase
        self.cleaned_data['category_name'] = normalized_name
        return normalized_name


class AddTagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['tag']

    def clean_tag(self):
        tag = self.cleaned_data['tag'].strip()
        normalized_tag = tag.lower()

        if Tag.objects.filter(tag__iexact=tag).exists():
            raise ValidationError(f"A tag with the name '{
                                  tag}' already exists.")

        # Normalize the tag to lowercase
        self.cleaned_data['tag'] = normalized_tag
        return normalized_tag


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['title', 'author', 'content', 'category', 'tags', 'image']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Post Title'}),
            'author': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Author Name'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
