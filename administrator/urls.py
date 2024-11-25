from django.urls import path
from . import views

urlpatterns = [
    path('all-products', views.AllProductsView, name='all-products'),
    path('all-categories', views.AllCategoriesView, name='all-categories'),
    path('all-tags', views.AllTagsView, name='all-tags'),
    path('add-product', views.AddProductView, name='add-product'),
    path('add-tag', views.AddTagView, name='add-tag'),
    path('edit-product/<int:product_id>',
         views.EditProductView, name='edit-product'),
    path('edit-category/<int:category_id>',
         views.EditCategoryView, name='edit-category'),
    path('edit-tag/<int:tag_id>',
         views.EditTagView, name='edit-tag'),
    path('delete-product/<int:product_id>',
         views.DeleteProductsView, name='delete-product'),
    path('delete-category/<int:category_id>',
         views.DeleteCategoryView, name='delete-category'),
    path('delete-tag/<int:tag_id>',
         views.DeleteTagView, name='delete-tag'),
    path('add-category', views.AddCategoryView, name='add-category'),

]
