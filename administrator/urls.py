from django.urls import path
from . import views

urlpatterns = [
    path('all-products', views.AllProductsView, name='all-products'),
    path('add-product', views.AddProductView, name='add-product'),
    path('add-category', views.AddCategoryView, name='add-category'),

]
