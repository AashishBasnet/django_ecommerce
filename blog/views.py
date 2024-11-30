from django.shortcuts import render, get_object_or_404
from .models import Post, Category, Tag


def AllBlogsView(request):
    posts = Post.objects.all().order_by('-id')
    return render(request, "blog/all_blogs_template.html", {'posts': posts})


def SingleBlogView(request, slug):
    post = get_object_or_404(Post, slug=slug)
    previous_post = Post.objects.filter(id=post.id-1).first()
    next_post = Post.objects.filter(id=post.id + 1).first()
    all_posts = Post.objects.all()
    return render(request, "blog/single_blog_template.html",
                  {"post": post,
                   "all_posts": all_posts,
                   "previous_post": previous_post,
                   "next_post": next_post
                   })
