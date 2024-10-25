from django.urls import path
from . import views

urlpatterns = [
    path("", views.HomeView, name='home'),
    path("about/", views.AboutView, name='about'),
    path("login/", views.UserLoginView, name='login'),
    path("logout/", views.UserLogoutView, name='logout'),
    path("register/", views.UserRegisterView, name='register'),
    path("update-password/", views.UpdatePasswordView, name='update-password'),
    path("product/<slug:slug>", views.SingleProductView, name='product'),
    path("category/<slug>", views.ProductCategoryView, name='category'),
    path("update-user/", views.UpdateUserView, name='update-user'),
    path("update-info/", views.UpdateUserInfoView, name='update-info'),
]
