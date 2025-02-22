from django.urls import path
from . import views

urlpatterns = [
    path("", views.HomeView, name='home'),
    path("shop", views.ShopView, name='shop'),
    path("about/", views.AboutView, name='about'),
    path("login/", views.UserLoginView, name='login'),
    path("logout/", views.UserLogoutView, name='logout'),
    path("register/", views.UserRegisterView, name='register'),
    path("update-password/", views.UpdatePasswordView, name='update-password'),
    path("product/<slug:slug>", views.SingleProductView, name='product'),
    path("category/<slug>", views.ProductCategoryView, name='category'),
    path("tags/<slug>", views.ProductTagView, name='tags'),
    path("update-user/", views.UpdateUserView, name='update-user'),
    path("update-info/", views.UpdateUserInfoView, name='update-info'),
    path("search/", views.SearchView, name='search'),
    path("contact/", views.ContactView, name='contact'),
    path("all-reviews/<slug:slug>", views.AllReviewsView, name='all-reviews'),
    path('delete-user-review/<int:review_id>',
         views.DeleteUserReviewView, name='delete-user-review'),
    path("user-dashboard", views.UserDashboardView, name='user-dashboard'),
    path("order-history", views.UserOrderHistoryView, name='order-history'),
    path("user-orders/<int:pk>",
         views.UserOrdersView, name="user-orders"),

]
