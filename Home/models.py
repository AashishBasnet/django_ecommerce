from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator, ValidationError
import datetime
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from tinymce.models import HTMLField


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_modified = models.DateTimeField(auto_now=True)
    phone = models.CharField(max_length=10, blank=True, validators=[
        RegexValidator(
            regex=r'^\d{10}$',
            message="Phone number must be exactly 10 digits."
        )])
    address1 = models.CharField(max_length=200, blank=True)
    address2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=200, blank=True)
    state = models.CharField(max_length=200, blank=True)
    zipcode = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=200, blank=True)
    old_cart = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.user.username

# create a user profile by default when user signs up


def create_profile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile(user=instance)
        user_profile.save()

# Automate the profile


post_save.connect(create_profile, sender=User)


class Tag(models.Model):
    tag = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.tag
    slug = models.SlugField(unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.tag)
        super().save(*args, **kwargs)
# categories of Products


class Categories(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    category_display_image = models.ImageField(
        upload_to='uploads/product/', null=True)
    slug = models.SlugField(unique=True, blank=True, null=True)

    def __str__(self):
        return self.category_name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.category_name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'categories'


class Customer(models.Model):
    customer_first_name = models.CharField(max_length=50)
    customer_last_name = models.CharField(max_length=50)
    customer_phone_number = models.CharField(max_length=10, blank=True, validators=[
        RegexValidator(
            regex=r'^\d{10}$',
            message="Phone number must be exactly 10 digits."
        )
    ]
    )
    customer_email = models.EmailField(max_length=100)
    customer_password = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.customer_first_name} {self.customer_last_name}'


class Product(models.Model):
    product_name = models.CharField(max_length=50, unique=True)
    product_price = models.DecimalField(
        decimal_places=2, max_digits=8, blank=False, null=False)
    product_category = models.ForeignKey(
        Categories, on_delete=models.CASCADE, default='')
    product_description = models.CharField(
        max_length=250, default='', blank=True, null=True)
    product_long_description = HTMLField(blank=True, null=True)
    product_additional_information = models.TextField(
        max_length=500, default='', blank=True, null=True)
    product_image = models.ImageField(upload_to='uploads/product/', null=True)

    product_tag = models.ManyToManyField(Tag, blank=True)
    product_rating = models.DecimalField(
        decimal_places=1, max_digits=3,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        null=True, blank=False
    )
    product_sale_price = models.DecimalField(
        decimal_places=2, max_digits=8, null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)

    def clean(self):
        super().clean()
        if self.product_sale_price is not None and self.product_sale_price > self.product_price:
            raise ValidationError(
                'Discount price cannot be greater than the actual price.')

    def save(self, *args, **kwargs):
        # Ensure slug is created
        if not self.slug:
            self.slug = slugify(self.product_name)

        super().save(*args, **kwargs)

        # Sale Tag
        sale_tag, _ = Tag.objects.get_or_create(tag='Sale')
        if self.product_sale_price:
            self.product_tag.add(sale_tag)
        else:
            self.product_tag.remove(sale_tag)

        #  New Tag to the 5 most recent products
        new_tag, _ = Tag.objects.get_or_create(tag='New')
        recent_products = Product.objects.order_by('-id')[:5]
        if self in recent_products:
            self.product_tag.add(new_tag)
        else:
            self.product_tag.remove(new_tag)

    def __str__(self):
        return f'{self.product_name}'


class Order(models.Model):
    order_product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order_customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_quantity = models.IntegerField(default=1)
    order_address = models.CharField(max_length=100, default='', blank=True)
    order_phone_number = models.CharField(max_length=10, blank=True, validators=[
        RegexValidator(
            regex=r'^\d{10}$',
            message="Phone number must be exactly 10 digits."
        )
    ]
    )
    order_date = models.DateField(default=datetime.date.today)
    order_status = models.BooleanField(default=False)

    def __str__(self):
        return self.order_product


class Inquiry(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    subject = models.CharField(max_length=150)
    message = models.TextField()

    def __str__(self):
        return f"Inquiry from {self.name} - {self.subject}"

    class Meta:
        verbose_name = 'User Inquires'
