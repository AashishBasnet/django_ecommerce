from django.shortcuts import render, get_object_or_404, redirect
from .cart import Cart
from Home.models import Product
from django.http import JsonResponse
from django.contrib import messages


# Create your views here.


def CartSummaryView(request):

    # Get Cart
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    subtotal = cart.cart_sub_total()
    # Calculate total
    totals = cart.cart_total()
    return render(request, "cart/cart_summary_template.html", {
        "cart_products": cart_products,
        "quantities": quantities,
        "totals": totals,
        "subtotal": subtotal
    })


def CartAddView(request):
    # get the cart
    cart = Cart(request)
    # test for POST
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))
        product = get_object_or_404(Product, id=product_id)
        # save to session
        cart.add(product=product, quantity=product_qty)
        # get cart quantity
        cart_quantity = cart.__len__()
        # response = JsonResponse({
        #     'Product Name' : product.product_name })

        response = JsonResponse({
            'qty': cart_quantity})
        messages.success(request, ("Product added to cart"))
        return response


def CartDeleteView(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        # Call delete Function in Cart
        cart.delete(product=product_id)

        response = JsonResponse({'product': product_id})
        messages.success(request, ("Item deleted from cart"))
        return response


def CartUpdateView(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))

        cart.update(product=product_id, quantity=product_qty)
        response = JsonResponse({'qty': product_qty})
        messages.success(request, ("Your cat has been updated"))
        return response
