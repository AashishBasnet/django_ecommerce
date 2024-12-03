from django.urls import path
from . import views

urlpatterns = [
    path("", views.AllBlogsView, name='blog'),
    path("blog-category/<slug:slug>",
         views.BlogCategoryView, name='blog-category'),
    path("blog-tag/<slug:slug>", views.BlogTagView, name='blog-tag'),
    path("<slug:slug>", views.SingleBlogView, name='single-blog'),
    path("blog-search/", views.BlogSearchView, name='blog-search'),

]
