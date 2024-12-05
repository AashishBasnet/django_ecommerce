from .forms import InquiryForm
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from .models import Product, Categories, Profile, Tag
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm, InquiryForm
from payment.forms import ShippingForm
from payment.models import ShippingAddress
from django import forms
from django.db.models import Q
from cart.cart import Cart
import json
import math
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.


def HomeView(request):
    products = Product.objects.all()
    new_products = Product.objects.all().order_by('-id')[:5]
    tags = Tag.objects.all()
    discount = []
    for product in products:
        if product.product_sale_price:
            # Calculate discount percentage and format to two decimal places
            discount_percentage = (
                (product.product_price - product.product_sale_price) / product.product_price) * 100
            discount.append(float(f"{discount_percentage:.2f}"))

# Find the maximum discount percentage
    if discount:
        maximum_discount = max(discount)
        if maximum_discount % 10 < 5:
            round_max_discount = math.floor(maximum_discount / 5) * 5
        else:
            round_max_discount = math.ceil(maximum_discount / 10) * 10

    return render(request, "Home/home_template.html",
                  {
                      'products': products,
                      'tags': tags,
                      'discount_upto': round_max_discount,
                      'new_products': new_products
                  })


def ShopView(request):
    products_list = Product.objects.all()
    tags = Tag.objects.all()
    latest_products = Product.objects.all().order_by('-id')[:3]
    category_count = products_list.count()

    # Pagination setup
    paginator = Paginator(products_list, 9)  # Show 9 products per page
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, "Home/shop_template.html", {
        'products': products,
        'category_count': category_count,
        'latest_products': latest_products,
        'tags': tags,
    })


def AboutView(request):
    return render(request, "Home/about_template.html", {
    })


def UserLoginView(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            try:
                current_user = Profile.objects.get(user__id=request.user.id)
                saved_cart = current_user.old_cart
                if saved_cart:

                    converted_cart = json.loads(saved_cart)

                    cart = Cart(request)
                    for product_key, quantity in converted_cart.items():
                        cart.db_add(product=product_key, quantity=quantity)

            except Profile.DoesNotExist:
                pass

            messages.success(request, "You Have Been Logged In")

            return redirect("home")
        else:
            messages.warning(request, "There was an error logging you in")

            return redirect("login")
    else:
        return render(request, "Home/login_template.html", {})

# def UserLoginView(request):
#     if request.method == "POST":
#         username = request.POST['username']
#         password = request.POST['password']
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             login(request, user)
#             # Do some Shopping Cart stuff
#             current_user = Profile.objects.get(user__id=request.user.id)
#             # Get their saved cart from database
#             saved_cart = current_user.old_cart
#             # convert database string to python dictionary
#             if saved_cart:
#                 # convert to dictionary using JSON
#                 converted_cart = json.loads(saved_cart)
#                 # Add the loaded cart dictionary to our session
#                 cart = Cart(request)
#                 # Loop through the cart an add the items from database
#                 for key, value in converted_cart.items():
#                     cart.db_add(product=key, quantity=value)

#             messages.success(request, ("You Have Been Logged In"))
#             return redirect("home")
#         else:
#             messages.warning(request, ("There was a error logging you in"))
#             return redirect("login")
#     else:
#         return render(request, "Home/login_template.html", {})


def UserLogoutView(request):
    logout(request)
    messages.success(request, ("You are successfully logged out"))
    return redirect('home')


def UserRegisterView(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(
                request, ("User Created successfully, Please Fill Out Your Info Below"))
            return redirect('update-info')
        else:
            messages.warning(
                request, ("OOPS! There Was a Problem Logging You in. Please Try Again!"))
            return redirect('register')
    else:
        return render(request, "Home/register_template.html", {
            'form': form
        })


def SingleProductView(request, slug):
    tags = Tag.objects.all()

    product = get_object_or_404(Product, slug=slug)

    all_products = Product.objects.filter(
        product_category=product.product_category).order_by('-id')[:5]

    return render(request, "Home/single_product_template.html",
                  {
                      'products': product,
                      'all_products': all_products,
                      'tags': tags
                  })


def ProductCategoryView(request, slug):
    try:
        tags = Tag.objects.all()
        all_products = Product.objects.all()
        product_categories = Categories.objects.get(slug=slug)
        products = Product.objects.filter(product_category=product_categories)
        category_count = products.count()
        latest_products = Product.objects.all().order_by('-id')[:3]

        # Pagination setup
        paginator = Paginator(products, 9)  # Show 9 products per page
        page_number = request.GET.get('page')
        paginated_products = paginator.get_page(page_number)

        return render(request, 'Home/product_category_template.html', {
            'products': paginated_products,
            'product_categories': product_categories,
            'all_products': all_products,
            'category_count': category_count,
            'latest_products': latest_products,
            'tags': tags,
        })

    except Categories.DoesNotExist:
        messages.warning(request, "The Category Doesn't exist")
        return redirect('shop')


def ProductTagView(request, slug):
    try:
        tags = Tag.objects.all()
        all_products = Product.objects.all()
        product_tag = Tag.objects.get(slug=slug)
        products = Product.objects.filter(product_tag=product_tag)
        category_count = products.count()
        latest_products = Product.objects.all().order_by('-id')[:3]

        # Pagination setup
        paginator = Paginator(products, 9)  # 9 products per page
        page_number = request.GET.get('page')
        paginated_products = paginator.get_page(page_number)

        return render(request, 'Home/product_tags_template.html', {
            'products': paginated_products,
            'product_categories': product_tag,
            'all_products': all_products,
            'category_count': category_count,
            'latest_products': latest_products,
            'tags': tags,
        })

    except Tag.DoesNotExist:
        messages.warning(request, "The Tag Doesn't exist")
        return redirect('shop')


def UpdateUserView(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UpdateUserForm(request.POST or None, instance=current_user)
        if user_form.is_valid():
            user_form.save()

            login(request, current_user)
            messages.success(request, "Your Profile has been updated")
            return redirect('home')
        return render(request, "Home/update_user_template.html", {
            'user_form': user_form})

    else:
        messages.warning(request, "You must be logged in to access the page")
        return redirect('home')

    return render(request, "Home/update_user_template.html", {})


def UpdatePasswordView(request):
    if request.user.is_authenticated:
        current_user = request.user
        # did they fill out the form
        if request.method == 'POST':
            form = ChangePasswordForm(current_user, request.POST)
            # is the form valid
            if form.is_valid():
                form.save()
                messages.success(request, "Your Password has been updated ")
                login(request, current_user)
                return redirect('home')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    return redirect('update-password')

        else:
            form = ChangePasswordForm(current_user)
            return render(request, "Home/update_password_template.html", {"form": form})
    else:
        messages.warning(request, "You must be logged in to access the page")
        return redirect('home')


def UpdateUserInfoView(request):
    if request.user.is_authenticated:
        # Get current user
        current_user = Profile.objects.get(user__id=request.user.id)
        # Get current users shipping info
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)

        # Get original user form
        form = UserInfoForm(request.POST or None, instance=current_user)
        # get user shipping form
        shipping_form = ShippingForm(
            request.POST or None, instance=shipping_user)
        if form.is_valid() and shipping_form.is_valid():
            # save original form
            form.save()
            # save shipping form
            shipping_form.save()
            messages.success(request, "Your Info has been updated")
            return redirect('home')

        return render(request, "Home/update_user_info_template.html", {
            'form': form,
            'shipping_form': shipping_form})

    else:
        messages.warning(request, "You must be logged in to access the page")
        return redirect('home')


def SearchView(request):
    products = Product.objects.all()
    tags = Tag.objects.all()
    latest_products = Product.objects.all().order_by('-id')[:3]

    search_key = request.GET.get('s', '')

    # Redirect to shop if the search is empty
    if search_key == '':
        messages.warning(request, "Please enter a search term.")
        return redirect('shop')

    # Perform the search
    searched = Product.objects.filter(
        Q(product_name__icontains=search_key) |
        Q(product_description__icontains=search_key) |
        Q(product_category__category_name__icontains=search_key) |
        Q(product_tag__tag__icontains=search_key)
    ).distinct()

    # Redirect if no products were found
    if not searched.exists():
        messages.warning(
            request, "That product doesn't exist. Please try again.")
        return redirect('shop')

    # Create the paginator
    paginator = Paginator(searched, 9)  # Show 9 products per page
    page = request.GET.get('page')

    try:
        paginated_results = paginator.page(page)
    except PageNotAnInteger:
        paginated_results = paginator.page(1)
    except EmptyPage:
        paginated_results = paginator.page(paginator.num_pages)

    return render(request, "Home/search_template.html", {
        'search_key': search_key,
        'searched': paginated_results,  # Renamed here
        'products': products,
        'latest_products': latest_products,
        'tags': tags,
        'paginator': paginator
    })


def ContactView(request):
    if request.method == 'POST':
        form = InquiryForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            # Redirect or add success message here
            messages.success(request, ("Your inquiry has been submitted"))
            return redirect('contact')
    else:
        form = InquiryForm(user=request.user)
    return render(request, 'Home/contact_template.html', {'form': form})
