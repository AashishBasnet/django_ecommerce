from django.shortcuts import render, redirect, get_object_or_404
from Home.models import Product
from .forms import AddProductForm, AddCategoryForm
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


def DeleteProductsView(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # product deletion
    product.delete()

    # redirecting to all-products
    return redirect('all-products')


def AddProductView(request):
    if request.method == "POST":
        form = AddProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
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
            return redirect('all-products')
    else:
        form = AddProductForm(instance=product)
    return render(request, 'administrator/edit_product_template.html', {'form': form, 'product': product})


def AddCategoryView(request):
    if request.method == "POST":
        form = AddCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
        else:
            messages.warning(
                request, 'Please check the form for errors and try again.')
    else:
        form = AddCategoryForm()
    return render(request, "administrator/add_category_template.html", {"form": form})
