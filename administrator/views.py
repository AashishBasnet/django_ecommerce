from django.shortcuts import get_object_or_404, redirect
from Home.models import Product  # Import Product from Home app
from django.shortcuts import render, redirect, get_object_or_404
from Home.models import Product, Categories, Tag
from .forms import AddProductForm, AddCategoryForm, AddTagForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from Home.models import Profile


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
            form.save()
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
            form.save()
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
            form.save()
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
