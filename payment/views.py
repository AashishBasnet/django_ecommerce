from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.core.cache import cache
from django.dispatch import receiver
from paypal.standard.ipn.signals import valid_ipn_received
from django.core.exceptions import ObjectDoesNotExist
from Home.models import Product
from django.shortcuts import render
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
from django.core.paginator import Paginator
from paypal.standard.models import ST_PP_COMPLETED
import hmac
import hashlib
import base64
from django.http import JsonResponse
import json


def genSha256(key, message):
    key = key.encode('utf-8')
    message = message.encode('utf-8')

    hmac_sha256 = hmac.new(key, message, hashlib.sha256)
    digest = hmac_sha256.digest()

    # Convert the digest to a Base64-encoded string
    signature = base64.b64encode(digest).decode('utf-8')

    return signature


def get_exchange_rate():
    url = "https://open.er-api.com/v6/latest/NPR"
    try:
        # Add a timeout to prevent hanging
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        return Decimal(data['rates']['USD'])
    except (requests.ConnectionError, requests.Timeout) as e:
        print(f"Connection error: {e}")

        return "Connection Timeout"
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise


def BillingInfoView(request):
    esewa_my_shipping = request.POST
    request.session['my_shipping'] = esewa_my_shipping

    # Gather order info
    esewa_full_name = esewa_my_shipping['shipping_full_name']
    esewa_email = esewa_my_shipping['shipping_email']

    # create shipping address from session info
    esewa_shipping_address = f"{esewa_my_shipping['shipping_address1']}\n{esewa_my_shipping['shipping_address2']}\n{esewa_my_shipping['shipping_city']}\n{
        esewa_my_shipping['shipping_state']}\n{esewa_my_shipping['shipping_zipcode']}\n{esewa_my_shipping['shipping_country']}"

    esewa_host = request.get_host()
    esewa_success_url = f'http://{esewa_host}{reverse("payment-success")}'
    esewa_failure_url = f'http://{esewa_host}{reverse("payment-failed")}'
    key = '8gBm/:&EnhH.1/q'
    uid = str(uuid.uuid4())
    esewa_cart = Cart(request)
    esewa_cart_products = esewa_cart.get_prods
    esewa_quantities = esewa_cart.get_quants
    esewa_totals = esewa_cart.cart_total()
    esewa_totals_without_vat = esewa_cart.cart_total_without_vat()
    esewa_vat = esewa_totals - esewa_totals_without_vat
    message = f'total_amount={esewa_totals},transaction_uuid={
        uid},product_code=EPAYTEST'
    signature = genSha256(key, message)

    user = request.user
    # create Order
    create_order = Order(user=user, full_name=esewa_full_name, email=esewa_email,
                         shipping_address=esewa_shipping_address, amount_paid=esewa_totals, invoice=uid, epay=True)
    create_order.save()

    # Add order items
    # get the order id
    order_id = create_order.pk
    # get product Info
    for product in esewa_cart_products():
        # get id
        product_id = product.id
        # get price
        if product.product_sale_price and product.product_sale_price > 0:
            price = product.product_sale_price
        else:
            price = product.product_price
            # get quantity
        for key, value in esewa_quantities().items():
            if int(key) == product.id:
                # create order item
                create_order_item = OrderItem(
                    order_id=order_id, product_id=product_id, user=user, quantity=value, price=price)
                create_order_item.save()

            # delete cart from database (old_cart_field)
    current_user = Profile.objects.filter(user__id=request.user.id)
    # delete shopping cart in db (old_cart field)
    current_user.update(old_cart="")

    if request.POST:
        cart = Cart(request)
        cart_products = cart.get_prods
        quantities = cart.get_quants
        totals = cart.cart_total()
        exchange_rate = get_exchange_rate()

        if exchange_rate == "Connection Timeout":
            messages.warning(
                request, "Unable to fetch the exchange rate. Please check your internet connection.")
            return redirect('checkout')

        # Convert totals from NPR to USD
        amount_in_usd = (totals * exchange_rate)
        amount_in_usd = format(amount_in_usd, '.2f')
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
                "billing_form": billing_form,
                'signature': signature,
                'uid': uid,
                'esewa_totals': esewa_totals,
                'esewa_totals_without_vat': esewa_totals_without_vat,
                'esewa_vat': esewa_vat,
                'esewa_success_url': esewa_success_url,
                'esewa_failure_url': esewa_failure_url
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
                "billing_form": billing_form,
                'signature': signature,
                'uid': uid,
                'esewa_totals': esewa_totals,
                'esewa_totals_without_vat': esewa_totals_without_vat,
                'esewa_vat': esewa_vat,
            })

    else:
        messages.success(request, "Access Denied")
        return redirect('home')


def is_valid_base64(s):
    try:
        base64.b64decode(s)
        return True
    except base64.binascii.Error:
        return False


@receiver(valid_ipn_received)
def handle_paypal_ipn(sender, **kwargs):
    # Extract the IPN object sent by PayPal
    ipn_obj = sender

    # Retrieve the invoice
    invoice = ipn_obj.invoice

    # You can store the invoice in a temporary cache or session if needed
    # Example with cache (requires django.core.cache)

    cache.set(f"paypal_invoice_{sender}", invoice, timeout=3600)


def PaymentSuccessView(request):
    # Decode and process Base64-encoded 'data' parameter
    encoded_data = request.GET.get('data', None)
    decoded_data = {}
    paypal_payer = request.GET.get('PayerID', None)

    if paypal_payer is None and encoded_data is None:
        # If neither payment method is used, restrict access
        messages.warning(
            request, "Unauthorized access: No payment data provided.")
        return redirect('home')
    else:
        payment_done = True
    if encoded_data:
        if is_valid_base64(encoded_data):
            try:
                # Decode Base64 and parse JSON
                decoded_bytes = base64.b64decode(encoded_data)
                decoded_string = decoded_bytes.decode(
                    'utf-8')  # Decode as UTF-8
                decoded_data = json.loads(decoded_string)  # Parse JSON

                my_Invoice = str(decoded_data['transaction_uuid'])
                try:
                    # Look up the order based on the esewa invoice
                    my_Order = Order.objects.get(invoice=my_Invoice)

                    # Check if the payment status is completed
                    if decoded_data['status'] == "COMPLETE":
                        my_Order.paid = True
                        my_Order.save()

                except ObjectDoesNotExist:
                    print(f"Order with invoice {my_Invoice} not found.")

            except (base64.binascii.Error, json.JSONDecodeError, UnicodeDecodeError) as e:
                # Handle decoding errors or invalid JSON
                print(f"Error processing payment data: {e}")
                messages.warning(request, "Failed to process payment data.")
                return redirect('home')  # Redirect to home if decoding fails
        else:
            messages.warning(request, "Invalid payment data.")
            return redirect('home')

    # Log or process the decoded data if needed

    # Check the cart
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    cart_totals = cart.cart_total()
    render_cart_products = cart_products
    render_cart_quantities = quantities
    render_cart_totals = cart_totals

    # Decrease stock for purchased products
    for product in cart_products():
        product_id = product.id
        quantity = quantities().get(str(product_id), 0)

        # Check and update stock
        if product.stock >= quantity:
            product.stock -= quantity
            product.save()
        else:
            messages.warning(request, f"Not enough stock for {
                             product.product_name}.")
            return redirect('home')  # Redirect to cart in case of stock issue

    # Clear the cart
    for key in list(request.session.keys()):
        if key == 'session_key':
            del request.session[key]

    # Success message
    messages.success(
        request, "Payment successful! Your order has been placed.")
    # Render success template and pass the decoded data
    return render(request, "payment/payment_success_template.html", {"decoded_data": decoded_data,
                                                                     "cart_products": render_cart_products,
                                                                     "quantities": render_cart_quantities,
                                                                     "totals": render_cart_totals,
                                                                     'payment_done': payment_done
                                                                     })


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
        # Filter orders that are not shipped and paid
        orders = Order.objects.filter(
            shipped=False, paid=True).order_by('-date_ordered')
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
        paginator = Paginator(orders, 15)
        page_number = request.GET.get('page')
        order_page = paginator.get_page(page_number)
        return render(request, "payment/not_shipped_dashboard_template.html", {"orders": order_page})
    else:
        messages.success(
            request, "Access Denied! only authorized users can view this page.")
        return redirect('home')


def ShippedDashboardView(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(
            shipped=True, paid=True).order_by('-date_shipped')
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
        paginator = Paginator(orders, 15)
        page_number = request.GET.get('page')
        order_page = paginator.get_page(page_number)
        return render(request, "payment/shipped_dashboard_template.html", {"orders": order_page})
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
