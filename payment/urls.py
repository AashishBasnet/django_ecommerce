from django.urls import path
from . import views

urlpatterns = [
    path("payment-success", views.PaymentSuccessView, name='payment-success'),
    path("checkout", views.CheckoutView, name='checkout'),
    path("billing-info", views.BillingInfoView, name='billing-info'),
    path("process-order", views.ProcessOrderView, name='process-order'),


]
