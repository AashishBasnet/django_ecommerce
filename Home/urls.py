from django.urls import path
from . import views

urlpatterns = [
    path("", views.HomeView, name= 'home'),
    path("about/", views.AboutView, name='about'),
    path("login/", views.UserLoginView, name='login'),
    path("logout/", views.UserLogoutView, name='logout'),
    path("register/", views.UserRegisterView, name='register'),
    path("product/<slug:slug>", views.SingleProductView, name='product'),
    path("category/<slug>", views.ProductCategoryView, name='category'),

]
