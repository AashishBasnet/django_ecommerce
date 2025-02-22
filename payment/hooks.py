from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
from django.conf import settings
import time
from .models import Order

from django.core.exceptions import ObjectDoesNotExist
import time


@receiver(valid_ipn_received)
def paypal_payment_received(sender, **kwargs):
    # add a 5-second pause for PayPal to send IPN data
    time.sleep(5)

    # grab the info that PayPal sends
    paypal_obj = sender

    # Grab the invoice
    my_Invoice = str(paypal_obj.invoice)

    try:
        # Look up the order based on the PayPal invoice
        my_Order = Order.objects.get(invoice=my_Invoice)

        # Check if the payment status is completed
        if paypal_obj.payment_status == "Completed":
            my_Order.paid = True
            my_Order.save()
            print(f"Order {my_Order.id} marked as paid.")
        else:
            print(f"Payment status for Order {my_Order.id} is not completed.")

    except ObjectDoesNotExist:
        print(f"Order with invoice {my_Invoice} not found.")

    except Exception as e:
        print(f"Error processing IPN: {str(e)}")
