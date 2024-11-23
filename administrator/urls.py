from django.urls import path
from . import views

urlpatterns = [
    path('all-products', views.AllProductsView, name='all-products'),
    path('all-categories', views.AllCategoriesView, name='all-categories'),
    path('add-product', views.AddProductView, name='add-product'),
    path('edit-product/<int:product_id>',
         views.EditProductView, name='edit-product'),
    path('edit-category/<int:category_id>',
         views.EditCategoryView, name='edit-category'),
    path('delete-product/<int:product_id>',
         views.DeleteProductsView, name='delete-product'),
    path('delete-category/<int:category_id>',
         views.DeleteCategoryView, name='delete-category'),
    path('add-category', views.AddCategoryView, name='add-category'),

]
