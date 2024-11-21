from django.urls import path
from . import views

urlpatterns = [
    path('add-product', views.AddProductView, name='add-product'),
]
