from django.utils.text import slugify
from Home.models import Product  # Import Product from Home app
from django.shortcuts import render, redirect, get_object_or_404
from Home.models import Product, Categories, Tag
from .forms import AddProductForm, AddCategoryForm, AddTagForm, PostForm, AddBlogCategoryForm, AddBlogTagForm
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from Home.models import Profile, Inquiry
from django.db.models import Q
from blog.models import Post, Category, Tag as T
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist

# View for adding a new post


def DashboardView(request):
    users = User.objects.filter(is_superuser=False)
    user_inquiry = Inquiry.objects.filter(is_reviewed=False)
    inquiry_count = 0
    user_count = 0
    for user in users:
        user_count += 1
    for inquiry in user_inquiry:
        inquiry_count += 1
    return render(request, "administrator/admin_dashboard_template.html", {'user_count': user_count, 'inquiry_count': inquiry_count})


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
