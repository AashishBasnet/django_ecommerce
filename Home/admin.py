from django.contrib import admin
from .models import Categories, Customer, Product, Order, Tag, Profile, Inquiry
from django.contrib.auth.models import User
# Register your models here.

admin.site.register(Categories)
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Tag)
admin.site.register(Profile)
admin.site.register(Inquiry)

# mix up the profile model with user model or merge the infos


class ProfileInline(admin.StackedInline):
    model = Profile


class UserAdmin(admin.ModelAdmin):
    model = User
    field = ["username", "first_name", "last_name", "email"]
    inlines = [ProfileInline]


# unregister the old registering way
admin.site.unregister(User)
# re-register the new registering way
admin.site.register(User, UserAdmin)
