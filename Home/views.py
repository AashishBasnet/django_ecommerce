from django.shortcuts import render, redirect
from django.http import Http404
from .models import Product, Categories
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm
from django import forms
# Create your views here.


def HomeView(request):
    products = Product.objects.all()
    categories = Categories.objects.all()
    return render(request, "Home/home_template.html",
                  {
                      'products': products,
                      'categories': categories,
                  })


def AboutView(request):
    return render(request, "Home/about_template.html")


def UserLoginView(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
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
            messages.success(request, ("You have registered successfully"))
            return redirect('home')
        else:
            messages.success(
                request, ("OOPS! There Was a Problem Logging You in. Please Try Again!"))
            return redirect('register')
    else:
        return render(request, "Home/register_template.html", {
            'form': form
        })


def SingleProductView(request, slug):
    product = Product.objects.get(slug=slug)
    return render(request, "Home/single_product_template.html",
                  {
                      'products': product
                  })


def ProductCategoryView(request, slug):

    try:
        product_categories = Categories.objects.get(slug = slug)
        products = Product.objects.filter(product_category = product_categories)
        categories = Categories.objects.all()
        return render(request, 'Home/product_category_template.html',
                      {
                          'products': products,
                          'product_categories': product_categories,
                          'categories' : categories
                      })


    except:
        messages.success(request, ("The Category Doesn't exist"))
        return redirect('home')
