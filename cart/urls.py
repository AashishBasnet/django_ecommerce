from django.urls import path
from . import views

urlpatterns = [
    path("", views.CartSummaryView, name= 'cart-summary'),
    path("add/", views.CartAddView, name= 'cart-add'),
    path("delete/", views.CartDeleteView, name= 'cart-delete'),
    path("update/", views.CartUpdateView, name= 'cart-update'),

]
