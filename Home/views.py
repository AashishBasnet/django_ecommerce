from django.shortcuts import render, redirect
from django.http import Http404
from .models import Product, Categories, Profile
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm
from payment.forms import ShippingForm
from payment.models import ShippingAddress
from django import forms
from django.db.models import Q
from cart.cart import Cart
import json
# Create your views here.


def HomeView(request):
    products = Product.objects.all()
    categories = Categories.objects.all()
    return render(request, "Home/home_template.html",
                  {
                      'products': products,
                      'categories': categories,
                  })


def ShopView(request):
    products = Product.objects.all()
    categories = Categories.objects.all()
    category_count = 0
    for category in products:
        category_count += 1
    return render(request, "Home/shop_template.html",
                  {
                      'products': products,
                      'categories': categories,
                      'category_count': category_count
                  })


def AboutView(request):
    categories = Categories.objects.all()

    return render(request, "Home/about_template.html", {
        'categories': categories,
    })


def UserLoginView(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Do some Shopping Cart stuff
            current_user = Profile.objects.get(user__id=request.user.id)
            # Get their saved cart from database
            saved_cart = current_user.old_cart
            # convert database string to python dictionary
            if saved_cart:
                # convert to dictionary using JSON
                converted_cart = json.loads(saved_cart)
                # Add the loaded cart dictionary to our session
                cart = Cart(request)
                # Loop through the cart an add the items from database
                for key, value in converted_cart.items():
                    cart.db_add(product=key, quantity=value)

            messages.success(request, ("You Have Been Logged In"))
            return redirect("home")
        else:
            messages.success(request, ("There was a error logging you in"))
            return redirect("login")
    else:
        return render(request, "Home/login_template.html", {})


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
            messages.success(
                request, ("OOPS! There Was a Problem Logging You in. Please Try Again!"))
            return redirect('register')
    else:
        return render(request, "Home/register_template.html", {
            'form': form
        })


def SingleProductView(request, slug):
    categories = Categories.objects.all()

    product = Product.objects.get(slug=slug)
    all_products = Product.objects.all().order_by('-id')[:4]

    return render(request, "Home/single_product_template.html",
                  {
                      'products': product,
                      'all_products': all_products,
                      'categories': categories,
                  })


def ProductCategoryView(request, slug):

    try:
        all_products = Product.objects.all()
        product_categories = Categories.objects.get(slug=slug)
        products = Product.objects.filter(product_category=product_categories)
        categories = Categories.objects.all()
        category_count = 0
        for categories_counter in products:
            category_count += 1
        return render(request, 'Home/product_category_template.html',
                      {
                          'products': products,
                          'product_categories': product_categories,
                          'categories': categories,
                          'all_products': all_products,
                          'category_count': category_count
                      })

    except:
        messages.success(request, ("The Category Doesn't exist"))
        return redirect('home')


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
        messages.success(request, "You must be logged in to access the page")
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
        messages.success(request, "You must be logged in to access the page")
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
        messages.success(request, "You must be logged in to access the page")
        return redirect('home')


def SearchView(request):
    products = Product.objects.all()
    categories = Categories.objects.all()
    category_count = 0
    for category in products:
        category_count += 1

    # Checking if there's a search term in the GET parameters
    # Using 's' to match the form input name
    search_key = request.GET.get('s', '')

    if search_key:
        # Perform a search on the Product model
        searched = Product.objects.filter(
            Q(product_name__icontains=search_key) |
            Q(product_description__icontains=search_key) |
            Q(product_category__category_name__icontains=search_key)
        )

        # Show a message if no products were found
        if not searched.exists():
            messages.warning(
                request, "That product doesn't exist. Please try again.")

        return render(request, "Home/search_template.html", {
            'search_key': search_key,
            'searched': searched,
            'products': products,
            'categories': categories,
            'category_count': category_count
        })

    return render(request, "Home/search_template.html", {
        'products': products,
        'categories': categories,


    })
