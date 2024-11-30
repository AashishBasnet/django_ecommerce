from django.shortcuts import render, get_object_or_404
from .models import Post, Category, Tag
from django.core.paginator import Paginator, PageNotAnInteger


def AllBlogsView(request):
    posts = Post.objects.all().order_by('-id')
    paginator = Paginator(posts, 9)

    page = request.GET.get('page')
    try:
        posts_paginated = paginator.page(page)
    except PageNotAnInteger:
        posts_paginated = paginator.page(1)
    except EmptyPage:
        posts_paginated = paginator.page(paginator.num_pages)

    return render(request, "blog/all_blogs_template.html", {'posts': posts_paginated})


def SingleBlogView(request, slug):
    post = get_object_or_404(Post, slug=slug)
    previous_post = Post.objects.filter(id=post.id-1).first()
    next_post = Post.objects.filter(id=post.id + 1).first()
    all_posts = Post.objects.all()
    return render(request, "blog/single_blog_template.html",
                  {"post": post,
                   "all_posts": all_posts,
                   "previous_post": previous_post,
                   "next_post": next_post,
                   })
