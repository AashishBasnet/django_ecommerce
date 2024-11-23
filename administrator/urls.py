from django.urls import path
from . import views

urlpatterns = [
    path('all-products', views.AllProductsView, name='all-products'),
    path('add-product', views.AddProductView, name='add-product'),
    path('edit-product/<int:product_id>',
         views.EditProductView, name='edit-product'),
    path('delete-product/<int:product_id>',
         views.DeleteProductsView, name='delete-product'),
    path('add-category', views.AddCategoryView, name='add-category'),

]
