from django.shortcuts import render

# Create your views here.


def PaymentSuccessView(request):
    return render(request, "payment/payment_success_template.html", {})
