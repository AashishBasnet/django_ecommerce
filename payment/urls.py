from django.urls import path
from . import views

urlpatterns = [
    path("payment-success", views.PaymentSuccessView, name='payment-success'),
]
