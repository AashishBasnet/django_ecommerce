from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from Home.models import Product, Inquiry
from django.shortcuts import render, redirect, get_object_or_404
from Home.models import Product, Categories, Tag
from .forms import AddProductForm, AddCategoryForm, AddTagForm, PostForm, AddBlogCategoryForm, AddBlogTagForm, InquiryForm, AddBannerImageForm, AddHeroSectionImageForm
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from Home.models import Profile, Inquiry
from django.db.models import Q, Sum, F
from blog.models import Post, Category, Tag as T
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.utils.timezone import now
from datetime import timedelta, datetime
from payment.models import OrderItem, Order
from dateutil.relativedelta import relativedelta
import plotly.graph_objects as go
from html2image import Html2Image
from Home.models import BannerImage, HeroSectionImage
import os

# Function to determine the appropriate host dynamically


def get_django_home_url():
    ALLOWED_HOSTS = [
        '.vercel.app',
        '.now.sh',
        '127.0.0.1',
        'localhost',
        '53bc-2400-1a00-b060-1b87-a019-8bb1-92c4-e15b.ngrok-free.app'
    ]
    if os.getenv('ENV') == 'production':
        # Example: Use the first production host
        return f"https://{ALLOWED_HOSTS[0]}"
    elif os.getenv('ENV') == 'staging':
        # Example: Use staging host
        return f"https://{ALLOWED_HOSTS[1]}"
    else:
        # Default to localhost for development
        return f"http://{ALLOWED_HOSTS[2]}:8000/"


def DashboardView(request):
    today = now()
    hti = Html2Image()

    # Set the output directory
    output_dir = "static/images"
    hti.output_path = output_dir  # Specify the directory for saving files

    # Django homepage URL (replace with your actual function or URL)
    django_home_url = get_django_home_url()
    output_file = "homepage_screenshot.png"

    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory '{output_dir}'.")

    # Delete the previous screenshot if it exists
    full_output_path = os.path.join(output_dir, output_file)
    if os.path.exists(full_output_path):
        os.remove(full_output_path)
        print(f"Previous screenshot '{full_output_path}' deleted.")

    # Save the new screenshot
    hti.screenshot(
        url=django_home_url,
        save_as=output_file  # Only the filename, not the full path
    )

    print(f"New screenshot saved as '{full_output_path}'.")
    # Monthly Sales Data
    first_day_of_current_month = today.replace(day=1)
    this_month_orders = Order.objects.filter(
        paid=True,  # Only consider paid orders
        date_ordered__gte=first_day_of_current_month,
        date_ordered__lte=today
    )

    total_amount_this_month = sum(
        order_item.price * order_item.quantity
        for order in this_month_orders
        for order_item in OrderItem.objects.filter(order=order)
    )

    # Last 24 Hours Sales Data
    last_24_hours_orders = Order.objects.filter(
        paid=True,  # Only consider paid orders
        date_ordered__gte=today - timedelta(hours=24),
        date_ordered__lte=today
    )

    total_amount_last_24_hours = sum(
        order_item.price * order_item.quantity
        for order in last_24_hours_orders
        for order_item in OrderItem.objects.filter(order=order)
    )

    # Weekly Sales Data
    last_week_start = today - timedelta(weeks=1)

    # Daily Sales Data for Graph
    last_30_days = today - timedelta(days=30)
    daily_sales = (
        Order.objects.filter(
            paid=True,  # Only consider paid orders
            date_ordered__gte=last_30_days
        )
        .annotate(date=F("date_ordered__date"))
        .values("date")
        .annotate(total_sales=Sum("amount_paid"))
        .order_by("date")
    )

    dates = [entry["date"] for entry in daily_sales]
    sales = [entry["total_sales"] for entry in daily_sales]

    # Plotly Graph
    fig = go.Figure()
    fig.add_trace(go.Bar(x=dates, y=sales, name="Daily Sales"))
    fig.update_layout(

        xaxis_title="Date",
        yaxis_title="Total Sales (in NPR)",
        template="plotly_white",
        autosize=True,
    )
    # configuring plotly

    config = {
        "scrollZoom": True,
        "displayModeBar": True,
        "modeBarButtonsToRemove": [
            "lasso2d", "select2d", "autoScale2d", "hoverClosestCartesian",
            "hoverCompareCartesian", "resetScale2d", "pan2d", "toImage"
        ],
        "displaylogo": False,
    }

    graph_html = fig.to_html(full_html=False, config=config)

    # Additional Data
    users = User.objects.filter(is_superuser=False)
    user_count = users.count()
    user_inquiry = Inquiry.objects.filter(is_reviewed=False)
    inquiry_count = user_inquiry.count()
    users_last_week = User.objects.filter(
        is_superuser=False, date_joined__gte=last_week_start
    )
    user_count_last_week = users_last_week.count()
    user_change = user_count - user_count_last_week
    return render(request, "administrator/admin_dashboard_template.html", {
        'user_count': user_count,
        'user_change': user_change,
        'inquiry_count': inquiry_count,
        'sales_this_month': total_amount_this_month,
        'total_amount_last_24_hours': total_amount_last_24_hours,
        'sales_graph': graph_html,
    })


def WebsiteCustomizationView(request):
    # banner images
    banner_images = BannerImage.objects.all().order_by('-id')
    hero_section_images = HeroSectionImage.objects.all().order_by('-id')
    return render(request, "administrator/website_customization_template.html", {'banner_images': banner_images,
                                                                                 'hero_section_images': hero_section_images})


def AddBannerImageView(request):
    if request.method == 'POST':
        form = AddBannerImageForm(request.POST, request.FILES)
        if form.is_valid():

            banner = form.save()
            banner.save()
            messages.success(request, 'Banner was successfully added')
            return redirect('website-customization')
    else:
        form = AddBannerImageForm()
    return render(request, "administrator/add_banner_image_template.html", {'form': form})


def AddHeroSectionImageView(request):
    if request.method == 'POST':
        form = AddHeroSectionImageForm(request.POST, request.FILES)
        if form.is_valid():

            hero = form.save()
            hero.save()
            messages.success(request, 'Hero section was successfully added')
            return redirect('website-customization')
    else:
        form = AddHeroSectionImageForm()
    return render(request, "administrator/add_hero_image_template.html", {'form': form})


def EditBannerImageView(request, banner_id):
    banner_instance = get_object_or_404(BannerImage, id=banner_id)

    if request.method == 'POST':
        form = AddBannerImageForm(
            request.POST, request.FILES, instance=banner_instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Banner was successfully updated')
            return redirect('website-customization')
    else:
        form = AddBannerImageForm(instance=banner_instance)

    return render(request, "administrator/edit_banner_image_template.html", {'form': form, 'banner_instance': banner_instance})


def EditHeroSectionImageView(request, hero_section_id):
    hero_instance = get_object_or_404(HeroSectionImage, id=hero_section_id)

    if request.method == 'POST':
        form = AddHeroSectionImageForm(
            request.POST, request.FILES, instance=hero_instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hero section was successfully updated')
            return redirect('website-customization')
    else:
        form = AddHeroSectionImageForm(instance=hero_instance)

    return render(request, "administrator/edit_hero_image_template.html", {'form': form, 'hero_instance': hero_instance})


def DeleteBannerImageView(request, banner_id):
    banner = get_object_or_404(BannerImage, id=banner_id)

    # banner deletion
    banner.delete()
    messages.success(request, "Banner successfully deleted")
    # redirecting to website-customization
    return redirect('website-customization')


def DeleteHeroSectionImageView(request, hero_section_id):
    hero_section = get_object_or_404(HeroSectionImage, id=hero_section_id)

    # banner deletion
    hero_section.delete()
    messages.success(request, "Hero section successfully deleted")
    # redirecting to website-customization
    return redirect('website-customization')


def AllUsersView(request):
    user_list = User.objects.filter(is_superuser=False)
    paginator = Paginator(user_list, 20)

    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)

    return render(request, "administrator/all_users_template.html", {'users': users})


def UserInquiriesView(request):
    inquiry_list = Inquiry.objects.filter(is_reviewed=False).order_by('-id')
    paginator = Paginator(inquiry_list, 20)

    page_number = request.GET.get('page')
    inquiries = paginator.get_page(page_number)

    return render(request, "administrator/user_inquiries_template.html", {'inquiries': inquiries})


def SingleInquiryView(request, inquiry_id):
    inquiry = get_object_or_404(Inquiry, id=inquiry_id)
    if request.method == "POST":
        inquiry.is_reviewed = True
        inquiry.save()
        messages.success(request, "Inquiry was marked as read")
        return redirect('all-user-inquiries')
    return render(request, "administrator/single_inquiry_template.html", {"inquiry": inquiry})


def AddPostView(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():

            post = form.save()
            post.save()

            return redirect('admin-all-blogs')
    else:
        form = PostForm()
    return render(request, 'administrator/add_blog_template.html', {'form': form})


def EditBlogView(request, blog_id):
    blog = get_object_or_404(Post, id=blog_id)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            messages.success(request, "Blog post was successfully edited")
            return redirect('admin-all-blogs')
    else:
        form = PostForm(instance=blog)
    return render(request, 'administrator/edit_blog_template.html', {'form': form, 'blog': blog})


def AllBlogsView(request):
    # Assuming `created_at` is a field for ordering
    blogs_list = Post.objects.all().order_by('-created_at')
    paginator = Paginator(blogs_list, 10)  # Paginate 10 blogs per page
    page_number = request.GET.get('page')
    blogs = paginator.get_page(page_number)
    return render(request, "administrator/all_blogs_template.html", {
        'blogs': blogs,
    })


def AllProductsView(request):
    products_list = Product.objects.all()
    paginator = Paginator(products_list, 15)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    return render(request, "administrator/all_products_template.html", {
        'products': products,
    })


def AllCategoriesView(request):
    products_list = Categories.objects.all()
    paginator = Paginator(products_list, 15)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    return render(request, "administrator/all_categories_template.html", {
        'products': products,
    })


def AllTagsView(request):
    products_list = Tag.objects.all()
    paginator = Paginator(products_list, 15)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    return render(request, "administrator/all_tags_template.html", {
        'products': products,
    })


def DeleteProductsView(request, product_id):
    # Fetch the product
    product = get_object_or_404(Product, id=product_id)

    # If the user is logged in, handle the cart for their session
    if request.user.is_authenticated:
        try:
            # Get the current session's cart
            cart = request.session.get('session_key', {})

            # If the product exists in the cart, remove it
            if str(product_id) in cart:
                del cart[str(product_id)]  # Remove the product from the cart
                request.session['session_key'] = cart  # Update the session
                request.session.modified = True  # Mark session as modified
                messages.success(request, "Product removed from your cart.")

            # Also update the user's 'old_cart' field in the Profile model
            user_profile = Profile.objects.get(user=request.user)
            old_cart = user_profile.old_cart
            if old_cart:
                # Convert old_cart (which is a string) into a dictionary-like format
                cart_dict = eval(old_cart)
                if str(product_id) in cart_dict:
                    # Remove the product from the old_cart
                    del cart_dict[str(product_id)]

                # Convert the cart_dict back to a string and save it
                user_profile.old_cart = str(cart_dict)
                user_profile.save()

        except Exception as e:
            # Handle any session-related errors
            print(f"Error while updating cart: {e}")
            messages.error(
                request, "An error occurred while updating your cart.")

    # Delete the product from the database
    product.delete()

    # Notify the admin
    messages.success(
        request, "Product successfully deleted and removed from your cart"
    )

    # Redirect to the product listing page (or any page you want)
    return redirect('all-products')


def DeleteCategoryView(request, category_id):
    category = get_object_or_404(Categories, id=category_id)

    # category deletion
    category.delete()
    messages.success(request, "Category successfully deleted")
    # redirecting to all-categories
    return redirect('all-categories')


def DeleteTagView(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)

    # category deletion
    tag.delete()
    messages.success(request, "Tag successfully deleted")
    # redirecting to all-categories
    return redirect('all-tags')


def DeletePostView(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # category deletion
    post.delete()
    messages.success(request, "Post successfully deleted")
    # redirecting to all-posts
    return redirect('admin-all-blogs')


def AddProductView(request):
    if request.method == "POST":
        form = AddProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product successfully added")
            return redirect('all-products')
        else:

            messages.warning(
                request, 'Please check the form for errors and try again.')
    else:
        form = AddProductForm()
    return render(request, "administrator/add_product_template.html", {"form": form})


def EditProductView(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = AddProductForm(request.POST, request.FILES, instance=product)

        if form.is_valid():
            instance = form.save(commit=False)

            try:
                existing_product = Product.objects.get(
                    product_name=instance.product_name)

                if existing_product.id != instance.id:
                    existing_product.delete()

            except ObjectDoesNotExist:
                pass

            instance.save()
            form.save_m2m()
            messages.success(request, "Product was successfully edited")
            return redirect('all-products')

    else:
        form = AddProductForm(instance=product)

    return render(request, 'administrator/edit_product_template.html', {'form': form, 'product': product})


def EditCategoryView(request, category_id):
    category = get_object_or_404(Categories, id=category_id)
    if request.method == 'POST':
        form = AddCategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            instance = form.save(commit=False)
            try:
                existing_category = Categories.objects.get(
                    category_name=instance.category_name
                )
                if existing_category.id != instance.id:
                    existing_category.delete()
            except ObjectDoesNotExist:
                pass

            instance.save()
            messages.success(request, "Category was successfully edited")
            return redirect('all-categories')
    else:
        form = AddCategoryForm(instance=category)
    return render(request, 'administrator/edit_category_template.html', {'form': form, 'category': category})


def EditTagView(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)
    if request.method == 'POST':
        form = AddTagForm(request.POST, request.FILES, instance=tag)
        if form.is_valid():
            tag = form.save(commit=False)
            tag.slug = slugify(tag.tag)  # Update the slug based on the name
            tag.save()
            messages.success(request, "Tag was successfully edited")
            return redirect('all-tags')
    else:
        form = AddTagForm(instance=tag)
    return render(request, 'administrator/edit_tag_template.html', {'form': form, 'tag': tag})


def AddCategoryView(request):
    if request.method == "POST":
        form = AddCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Category successfully added")
            return redirect('all-categories')
        else:
            messages.warning(
                request, 'Please check the form for errors and try again.')
    else:
        form = AddCategoryForm()
    return render(request, "administrator/add_category_template.html", {"form": form})


def AddTagView(request):
    if request.method == "POST":
        form = AddTagForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Tag successfully added")
            return redirect('all-tags')
        else:
            messages.warning(
                request, 'Please check the form for errors and try again.')
    else:
        form = AddTagForm()
    return render(request, "administrator/add_tag_template.html", {"form": form})


def AdminSearchView(request):
    products = Product.objects.all()
    tags = Tag.objects.all()
    latest_products = Product.objects.all().order_by('-id')[:3]

    search_key = request.GET.get('s', '')

    # this redirects to shop if the search is empty
    if search_key == '':
        messages.warning(request, "Please enter a search term.")
        return redirect('all-products')

    # Perform the search
    searched = Product.objects.filter(
        Q(product_name__icontains=search_key) |
        Q(product_description__icontains=search_key) |
        Q(product_category__category_name__icontains=search_key) |
        Q(product_tag__tag__icontains=search_key)
    ).distinct()

    # this redirects if no products were found
    if not searched.exists():
        messages.warning(
            request, "That product doesn't exist. Please try again.")
        return redirect('all-products')

    # Create the paginator
    paginator = Paginator(searched, 15)  # This shows 15 products per page
    page = request.GET.get('page')

    try:
        paginated_results = paginator.page(page)
    except PageNotAnInteger:
        paginated_results = paginator.page(1)
    except EmptyPage:
        paginated_results = paginator.page(paginator.num_pages)

    return render(request, "administrator/admin_search_template.html", {
        'search_key': search_key,
        'searched': paginated_results,
        'products': products,
        'latest_products': latest_products,
        'tags': tags,
        'paginator': paginator
    })


def AllBlogCategoryView(request):
    categories = Category.objects.all().order_by(
        '-id')
    paginator = Paginator(categories, 15)
    page_number = request.GET.get('page')
    categories_page = paginator.get_page(page_number)
    return render(request, "administrator/all_blog_categories_template.html", {
        'categories': categories_page,
    })


def AddBlogCategoryView(request):
    if request.method == 'POST':
        form = AddBlogCategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.slug = slugify(category.name)
            category.save()
            messages.success(request, "Blog category successfully added")
            return redirect('all-blog-categories')
        else:
            messages.error(request, "Please correct the errors in the form")
    else:
        form = AddBlogCategoryForm()
    return render(request, 'administrator/add_blog_category_template.html', {'form': form})


def EditBlogCategoryView(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        form = AddBlogCategoryForm(request.POST, instance=category)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            messages.success(request, "Blog category successfully updated")
            return redirect('all-blog-categories')
        else:
            messages.error(request, "Please correct the errors in the form")
    else:
        form = AddBlogCategoryForm(instance=category)
    return render(request, 'administrator/edit_blog_category_template.html', {'form': form, 'category': category})


def DeleteBlogCategoryView(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    # blog category deletion
    category.delete()
    messages.success(request, "Category successfully deleted")
    # redirecting to all-categories
    return redirect('all-blog-categories')


def AllBlogTagView(request):
    tags = T.objects.all().order_by('-id')
    paginator = Paginator(tags, 15)
    page_number = request.GET.get('page')
    tags_page = paginator.get_page(page_number)
    return render(request, "administrator/all_blog_tags_template.html", {
        'tags': tags_page,
    })


def AddBlogTagView(request):
    if request.method == 'POST':
        form = AddBlogTagForm(request.POST)
        if form.is_valid():
            tag = form.save(commit=False)
            tag.slug = slugify(tag.name)
            tag.save()
            messages.success(request, "Tag successfully added")
            return redirect('all-blog-tags')  # Update this URL name as needed
        else:
            messages.error(request, "Please correct the errors in the form")
    else:
        form = AddBlogTagForm()
    return render(request, 'administrator/add_blog_tag_template.html', {'form': form})


def EditBlogTagView(request, tag_id):
    tag = get_object_or_404(T, id=tag_id)
    if request.method == 'POST':
        form = AddBlogTagForm(request.POST, instance=tag)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            messages.success(request, "Tag successfully updated")
            return redirect('all-blog-tags')  # Update this URL name as needed
        else:
            messages.error(request, "Please correct the errors in the form")
    else:
        form = AddBlogTagForm(instance=tag)
    return render(request, 'administrator/edit_blog_tag_template.html', {'form': form, 'tag': tag})


def DeleteBlogTagView(request, tag_id):
    tag = get_object_or_404(T, id=tag_id)

    # Tag deletion
    tag.delete()
    messages.success(request, "Tag successfully deleted")
    # Redirecting to all tags
    return redirect('all-blog-tags')  # Update this URL name as needed
