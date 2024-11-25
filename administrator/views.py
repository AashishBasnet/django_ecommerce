from django.shortcuts import render, redirect, get_object_or_404
from Home.models import Product, Categories, Tag
from .forms import AddProductForm, AddCategoryForm, AddTagForm
from django.contrib import messages
from django.core.paginator import Paginator


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
    product = get_object_or_404(Product, id=product_id)

    # product deletion
    product.delete()
    messages.success(request, "product successfully deleted")

    # redirecting to all-products
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
