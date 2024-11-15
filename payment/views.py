from django.shortcuts import render, redirect
from cart.cart import Cart
from .forms import ShippingForm, PaymentForm
from .models import ShippingAddress, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib import messages
from Home.models import Product, Profile
import datetime
# Create your views here.
# import some paypal stuff
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid  # unique user id for duplicate orders
import requests
from decimal import Decimal


def get_exchange_rate():
    url = "https://open.er-api.com/v6/latest/NPR"  # API endpoint
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        # Fetch the USD rate from the response
        return Decimal(data['rates']['USD'])
    else:
        raise Exception("Error fetching exchange rate")


def BillingInfoView(request):
    if request.POST:
        cart = Cart(request)
        cart_products = cart.get_prods
        quantities = cart.get_quants
        totals = cart.cart_total()
        exchange_rate = get_exchange_rate()

        # Convert totals from NPR to USD
        amount_in_usd = (totals * exchange_rate)
        amount_in_usd = format(amount_in_usd, '.2f')
        print(f"amount in usd: {amount_in_usd}")
        # create a session with shipping info
        my_shipping = request.POST
        request.session['my_shipping'] = my_shipping

        # Gather order info
        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email']

        # create shipping address from session info
        shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{
            my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}"
        amount_paid = totals

        # Get the Host
        host = request.get_host()
        # Create an invoice no
        my_Invoice = str(uuid.uuid4())
        # Create a PayPal Form Dictionary
        paypal_dict = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': amount_in_usd,
            'item_name': 'ecommerce Orders',
            'no_shipping': '2',
            'invoice': my_Invoice,
            'currency_code': 'USD',
            'notify_url': 'https://{}{}'.format(host, reverse("paypal-ipn")),
            'return_url': 'https://{}{}'.format(host, reverse("payment-success")),
            'cancel_return': 'https://{}{}'.format(host, reverse("payment-failed")),
        }
        # create paypal form
        paypal_form = PayPalPaymentsForm(initial=paypal_dict)
        # check to see if user is logged in
        if request.user.is_authenticated:
            # Get the billing form
            billing_form = PaymentForm()

            # logged in
            user = request.user
            # create Order
            create_order = Order(user=user, full_name=full_name, email=email,
                                 shipping_address=shipping_address, amount_paid=amount_paid, invoice=my_Invoice)
            create_order.save()

            # Add order items
            # get the order id
            order_id = create_order.pk
            # get product Info
            for product in cart_products():
                # get id
                product_id = product.id
                # get price
                if product.product_sale_price and product.product_sale_price > 0:
                    price = product.product_sale_price
                else:
                    price = product.product_price
                # get quantity
                for key, value in quantities().items():
                    if int(key) == product.id:
                        # create order item
                        create_order_item = OrderItem(
                            order_id=order_id, product_id=product_id, user=user, quantity=value, price=price)
                        create_order_item.save()

            # delete cart from database (old_cart_field)
            current_user = Profile.objects.filter(user__id=request.user.id)
            # delete shopping cart in db (old_cart field)
            current_user.update(old_cart="")

            return render(request, "payment/billing_info_template.html", {
                "paypal_form": paypal_form,
                "cart_products": cart_products,
                "quantities": quantities,
                "totals": totals,
                "shipping_info": request.POST,
                "billing_form": billing_form
            })

        else:
            # not logged in
            # create Order
            create_order = Order(full_name=full_name, email=email,
                                 shipping_address=shipping_address, amount_paid=amount_paid, invoice=my_Invoice)
            create_order.save()

            # Add order items
            # get the order id
            order_id = create_order.pk
            # get product Info
            for product in cart_products():
                # get id
                product_id = product.id
                # get price
                if product.product_sale_price and product.product_sale_price > 0:
                    price = product.product_sale_price
                else:
                    price = product.product_price
                # get quantity
                for key, value in quantities().items():
                    if int(key) == product.id:
                        # create order item
                        create_order_item = OrderItem(
                            order_id=order_id, product_id=product_id, quantity=value, price=price)
                        create_order_item.save()

            billing_form = PaymentForm()

            return render(request, "payment/billing_info_template.html", {
                "paypal_form": paypal_form,
                "cart_products": cart_products,
                "quantities": quantities,
                "totals": totals,
                "shipping_info": request.POST,
                "billing_form": billing_form
            })

    else:
        messages.success(request, "Access Denied")
        return redirect('home')


def PaymentSuccessView(request):
    # Delete the browser cart
    # get the cart
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()

  # delete cart
    for key in list(request.session.keys()):
        if key == 'session_key':
            # delete the key
            del request.session[key]

    return render(request, "payment/payment_success_template.html", {})


def PaymentFailedView(request):
    return render(request, "payment/payment_failed_template.html", {})


def CheckoutView(request):
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()
    sub_total = cart.cart_sub_total()

    if request.user.is_authenticated:
        # Checkout as logged in user

        # Shipping User
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
        # Shipping Form
        shipping_form = ShippingForm(
            request.POST or None, instance=shipping_user)
        return render(request, "payment/checkout_template.html", {
            "cart_products": cart_products,
            "quantities": quantities,
            "totals": totals,
            "subtotal": sub_total,
            "shipping_form": shipping_form
        })
    else:
        # Checkout as guest
        messages.warning(request, 'please login or register to continue')
        return redirect('login')

    return render(request, "payment/checkout_template.html", {})


def ProcessOrderView(request):
    if request.POST:
        # get the cart
        cart = Cart(request)
        cart_products = cart.get_prods
        quantities = cart.get_quants
        totals = cart.cart_total()
        payment_form = PaymentForm(request.POST or None)
        # get shipping session data
        my_shipping = request.session.get('my_shipping')

        # Gather order info
        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email']

        # create shipping address from session info
        shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{
            my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}"
        amount_paid = totals

        if request.user.is_authenticated:
            # logged in
            user = request.user
            # create Order
            create_order = Order(user=user, full_name=full_name, email=email,
                                 shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()

            # Add order items
            # get the order id
            order_id = create_order.pk
            # get product Info
            for product in cart_products():
                # get id
                product_id = product.id
                # get price
                if product.product_sale_price and product.product_sale_price > 0:
                    price = product.product_sale_price
                else:
                    price = product.product_price
                # get quantity
                for key, value in quantities().items():
                    if int(key) == product.id:
                        # create order item
                        create_order_item = OrderItem(
                            order_id=order_id, product_id=product_id, user=user, quantity=value, price=price)
                        create_order_item.save()
            # delete cart
            for key in list(request.session.keys()):
                if key == 'session_key':
                    # delete the key
                    del request.session[key]
            # delete cart from database (old_cart_field)
            current_user = Profile.objects.filter(user__id=request.user.id)
            # delete shopping cart in db (old_cart field)
            current_user.update(old_cart="")

            messages.success(request, "Order Placed!")
            return redirect('home')

        else:
            # not logged in
            # create Order
            create_order = Order(full_name=full_name, email=email,
                                 shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()

            # Add order items
            # get the order id
            order_id = create_order.pk
            # get product Info
            for product in cart_products():
                # get id
                product_id = product.id
                # get price
                if product.product_sale_price and product.product_sale_price > 0:
                    price = product.product_sale_price
                else:
                    price = product.product_price
                # get quantity
                for key, value in quantities().items():
                    if int(key) == product.id:
                        # create order item
                        create_order_item = OrderItem(
                            order_id=order_id, product_id=product_id, quantity=value, price=price)
                        create_order_item.save()

            # delete cart
            for key in list(request.session.keys()):
                if key == 'session_key':
                    # delete the key
                    del request.session[key]

            messages.success(request, "Order Placed!")
            return redirect('home')
    else:
        messages.warning(request, "Access Denied")
        return redirect('home')


def NotShippedDashboardView(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=False).order_by('-date_ordered')
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            # get the order
            order = Order.objects.filter(id=num)

            # grab date and time
            now = datetime.datetime.now()
            # update order
            order.update(shipped=True, date_shipped=now)
            # redirect
            messages.success(request, "Shipping Status Updated")
            return redirect('not-shipped-dashboard')

        return render(request, "payment/not_shipped_dashboard_template.html", {"orders": orders})
    else:
        messages.success(
            request, "Access Denied! only authorized users can view this page.")
        return redirect('home')


def ShippedDashboardView(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=True).order_by('-date_shipped')
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            # get the order
            order = Order.objects.filter(id=num)
            # grab date and time
            now = datetime.datetime.now()
            # update order
            order.update(shipped=False)
            # redirect
            messages.success(request, "Shipping Status Updated")
            return redirect('shipped-dashboard')
        return render(request, "payment/shipped_dashboard_template.html", {"orders": orders})
    else:
        messages.success(
            request, "Access Denied! only authorized users can view this page.")
        return redirect('home')


def OrdersView(request, pk):
    if request.user.is_authenticated and request.user.is_superuser:
        # get the order
        order = Order.objects.get(id=pk)
        # get the order items
        items = OrderItem.objects.filter(order=pk)

        if request.POST:
            status = request.POST['shipping_status']
            # check if true or false
            if status == "true":
                # get the order
                order = Order.objects.filter(id=pk)
                # update the status
                now = datetime.datetime.now()
                order.update(shipped=True, date_shipped=now)
                messages.success(request, "Shipping Status Updated")
                return redirect('not-shipped-dashboard')
            else:
                # get the order
                order = Order.objects.filter(id=pk)
                # update the status
                order.update(shipped=False)
            messages.success(request, "Shipping Status Updated")
            return redirect('shipped-dashboard')

        return render(request, 'payment/orders_template.html', {"order": order, "items": items})

    else:
        messages.success(
            request, "Access Denied! only authorized users can view this page.")
        return redirect('home')
