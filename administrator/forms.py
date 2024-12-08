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


class AddCategoryForm(forms.ModelForm):
    class Meta:
        model = Categories
        fields = [
            'category_name',
            'category_display_image',
        ]


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
