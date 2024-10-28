from django.urls import path
from . import views

urlpatterns = [
    path("payment-success", views.PaymentSuccessView, name='payment-success'),
    path("checkout", views.CheckoutView, name='checkout'),
    path("billing-info", views.BillingInfoView, name='billing-info'),
    path("process-order", views.ProcessOrderView, name='process-order'),
    path("shipped-dashboard", views.ShippedDashboardView, name='shipped-dashboard'),
    path("not-shipped-dashboard", views.NotShippedDashboardView,
         name='not-shipped-dashboard'),
    path("orders/<int:pk>", views.OrdersView, name="orders")
]
