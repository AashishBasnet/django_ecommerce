from .forms import InquiryForm
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.http import Http404
from .models import Product, Categories, Profile, Tag, BannerImage, UserReview, HeroSectionImage
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm, InquiryForm, UserReviewForm
from payment.forms import ShippingForm
from payment.models import ShippingAddress, Order, OrderItem
from django import forms
from django.db import models
from django.db.models import Q, Case, When, Value, F
from cart.cart import Cart
import json
import math
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from blog.views import Post
# Create your views here.
from django.db.models import Avg


def HomeView(request):

    reviews = UserReview.objects.all().order_by('-id')[:5]
    banner_images = BannerImage.objects.all().order_by('-id')
    hero_section_images = HeroSectionImage.objects.all().order_by('-id')
    products = Product.objects.all()
    posts = Post.objects.all().order_by('-id')[:3]
    new_products = Product.objects.all().order_by('-id')[:5]
    sale = Product.objects.filter(
        product_sale_price__isnull=False).order_by('-id')[:5]
    tags = Tag.objects.all()
    discount = []
    for product in products:
        if product.product_sale_price:
            discount_percentage = (
                (product.product_price - product.product_sale_price) / product.product_price) * 100
            discount.append(float(f"{discount_percentage:.2f}"))
    round_max_discount = 0
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
                      'new_products': new_products,
                      'posts': posts,
                      'banner_images': banner_images,
                      'reviews': reviews,
                      'hero_section_images': hero_section_images,
                      'sale': sale
                  })


# def ShopView(request):
#     products_list = Product.objects.all().order_by('-id')
#     tags = Tag.objects.all()
#     latest_products = Product.objects.all().order_by('-id')[:3]
#     category_count = products_list.count()
#     req = request.GET.get('q')
#     if req == 'newArrivals':
#         products_list = products_list
#     elif req == 'shopSale':
#         products_list = Product.objects.filter(
#             product_sale_price__isnull=False).order_by('-id')
#     elif req == 'price_asc':
#         products_list = Product.objects.annotate(
#             effective_price=Case(
#                 When(product_sale_price__isnull=True, then=F('product_price')),
#                 When(product_sale_price=0, then=F('product_price')),
#                 default=F('product_sale_price'),
#                 output_field=models.DecimalField()
#             )
#         ).order_by('effective_price')
#     elif req == 'price_desc':
#         products_list = Product.objects.annotate(
#             effective_price=Case(
#                 When(product_sale_price__isnull=True, then=F('product_price')),
#                 When(product_sale_price=0, then=F('product_price')),
#                 default=F('product_sale_price'),
#                 output_field=models.DecimalField()
#             )
#         ).order_by('-effective_price')
#     # Pagination setup
#     paginator = Paginator(products_list, 3)  # Show 9 products per page
#     page = request.GET.get('page')
#     try:
#         products = paginator.page(page)
#     except PageNotAnInteger:
#         products = paginator.page(1)
#     except EmptyPage:
#         products = paginator.page(paginator.num_pages)
#     return render(request, "Home/shop_template.html", {
#         'products': products,
#         'category_count': category_count,
#         'latest_products': latest_products,
#         'tags': tags,
#     })


def ShopView(request):
    products_list = Product.objects.all().order_by('-id')
    tags = Tag.objects.all()
    latest_products = Product.objects.all().order_by('-id')[:3]
    category_count = products_list.count()

    # Get the sorting/filtering option from the GET request
    req = request.GET.get('q')

    # Apply different filters based on the 'q' parameter
    if req == 'newArrivals':
        products_list = products_list
    elif req == 'shopSale':
        products_list = Product.objects.filter(
            product_sale_price__isnull=False).order_by('-id')
    elif req == 'price_asc':
        products_list = Product.objects.annotate(
            effective_price=Case(
                When(product_sale_price__isnull=True, then=F('product_price')),
                When(product_sale_price=0, then=F('product_price')),
                default=F('product_sale_price'),
                output_field=models.DecimalField()
            )
        ).order_by('effective_price')
    elif req == 'price_desc':
        products_list = Product.objects.annotate(
            effective_price=Case(
                When(product_sale_price__isnull=True, then=F('product_price')),
                When(product_sale_price=0, then=F('product_price')),
                default=F('product_sale_price'),
                output_field=models.DecimalField()
            )
        ).order_by('-effective_price')
    elif req == 'default':  # Handle default sorting
        products_list = Product.objects.all().order_by('-id')

    # Pagination setup
    paginator = Paginator(products_list, 9)  # Show 9 products per page
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    # Render the template with products and other context
    return render(request, "Home/shop_template.html", {
        'products': products,
        'category_count': category_count,
        'latest_products': latest_products,
        'tags': tags,
        'q': req,  # Pass 'q' parameter so it persists in the template
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
    user_reviews = UserReview.objects.filter(
        review_for__slug=slug).order_by('-id')[:2]
    product = get_object_or_404(Product, slug=slug)
    average_rating = UserReview.objects.filter(review_for__id=product.id).aggregate(Avg('rating'))[
        'rating__avg']
    all_products = Product.objects.filter(
        product_category=product.product_category).order_by('-id')[:5]
    average_rating = round(
        average_rating, 2) if average_rating is not None else None
    return render(request, "Home/single_product_template.html",
                  {
                      'products': product,
                      'all_products': all_products,
                      'tags': tags,
                      'user_reviews': user_reviews,
                      'average_rating': average_rating
                  })


def AllReviewsView(request, slug):
    product = get_object_or_404(Product, slug=slug)
    user_review = None
    verified_order = False
    average_rating = UserReview.objects.filter(review_for__id=product.id).aggregate(Avg('rating'))[
        'rating__avg']

    if request.user.is_authenticated:
        # Checking if the user has a verified order for this product or not
        orders = Order.objects.filter(user=request.user, paid=True)
        verified_order = OrderItem.objects.filter(
            order__in=orders, product=product
        ).exists()

        # Checking if the user has already reviewed the product
        user_review = UserReview.objects.filter(
            review_for=product, username=request.user.username
        ).first()

    # Handle form submission if conditions are met
    if request.method == 'POST' and not user_review and verified_order:
        form = UserReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.username = request.user.username
            review.review_for = product
            review.save()
            average_rating = UserReview.objects.filter(review_for__id=product.id).aggregate(Avg('rating'))[
                'rating__avg']
            return redirect('all-reviews', slug=slug)
    else:
        # Only showing the form if the user has a verified order
        form = UserReviewForm() if verified_order and not user_review else None

    reviews = UserReview.objects.filter(review_for=product).exclude(
        username=request.user.username
    ).order_by('-id')
    paginator = Paginator(reviews, 15)
    page_number = request.GET.get('page')
    reviews = paginator.get_page(page_number)
    average_rating = round(
        average_rating, 2) if average_rating is not None else None
    print(average_rating)
    return render(request, "Home/all_reviews_template.html", {
        'form': form,
        'reviews': reviews,
        'user_review': user_review,
        'verified_order': verified_order,
        'average_rating': average_rating
    })


def DeleteUserReviewView(request, review_id):
    review = get_object_or_404(UserReview, id=review_id, username=request.user)
    review.delete()
    slug = review.review_for.slug
    return redirect(reverse('all-reviews', kwargs={'slug': slug}))


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


def UserDashboardView(request):
    if request.user.is_authenticated:
        user_orders = Order.objects.filter(
            paid=True, user=request.user, shipped=False).order_by('-date_ordered')

    else:
        user_orders = None
        messages.warning(request, "Unauthorized Users cannot access this page")
        return redirect('home')
    paginator = Paginator(user_orders, 15)
    page_number = request.GET.get('page')
    order_page = paginator.get_page(page_number)
    return render(request, "Home/user_dashboard_template.html", {'user_orders': order_page})


def UserOrderHistoryView(request):
    if request.user.is_authenticated:
        user_orders = Order.objects.filter(
            paid=True, user=request.user, shipped=True).order_by('-date_ordered')
    else:
        user_orders = None
    paginator = Paginator(user_orders, 15)
    page_number = request.GET.get('page')
    order_page = paginator.get_page(page_number)
    return render(request, "Home/user_order_history_template.html", {'user_orders': order_page})


def UserOrdersView(request, pk):
    if request.user.is_authenticated:
        try:
            order = Order.objects.get(id=pk, user=request.user)
            items = OrderItem.objects.filter(order=order)
        except Order.DoesNotExist:
            order = None
            items = []
        return render(request, 'Home/user_orders_template.html', {"order": order, "items": items})
    else:
        messages.warning(
            request, "Access Denied! only logged in users can view this page.")
        return redirect('home')
