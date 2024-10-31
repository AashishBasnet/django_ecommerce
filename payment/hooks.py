from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
from django.conf import settings
import time
from .models import Order


@receiver(valid_ipn_received)
def paypal_payment_received(sender, **kwargs):
    # add a 5 second pause for paypal to send IPN data
    time.sleep(5)
    # grab the info that paypal sends
    paypal_obj = sender
    # Grab the invoice
    my_Invoice = str(paypal_obj.invoice)
    # match the paypal invoice to the order invoice
    # Look up the order
    my_Order = Order.objects.get(invoice=my_Invoice)
    # Record that the Order was paid
    my_Order.paid = True
    # save the Order
    my_Order.save()

    # print(paypal_obj)
    # print(f'Amount Paid: {paypal_obj.mc_gross}')
