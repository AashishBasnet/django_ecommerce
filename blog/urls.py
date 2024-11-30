from django.urls import path
from . import views

urlpatterns = [
    path("", views.AllBlogsView, name='blog'),
    path("<slug:slug>", views.SingleBlogView, name='single-blog'),
]
