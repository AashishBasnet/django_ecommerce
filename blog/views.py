from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Category, Tag
from django.core.paginator import Paginator, PageNotAnInteger
from django.contrib import messages
from django.db.models import Q


def AllBlogsView(request):
    posts = Post.objects.all().order_by('-id')
    latest_posts = Post.objects.all().order_by('-id')[:3]
    paginator = Paginator(posts, 9)
    tags = Tag.objects.all()
    all_categories = Category.objects.all()

    page = request.GET.get('page')
    try:
        posts_paginated = paginator.page(page)
    except PageNotAnInteger:
        posts_paginated = paginator.page(1)
    except EmptyPage:
        posts_paginated = paginator.page(paginator.num_pages)

    return render(request, "blog/all_blogs_template.html", {'posts': posts_paginated, 'all_categories': all_categories, 'tags': tags, 'latest_posts': latest_posts})


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


def BlogCategoryView(request, slug):
    try:
        category = get_object_or_404(Category, slug=slug)
        all_categories = Category.objects.all()
        posts = Post.objects.filter(category=category).order_by('-id')
        category_count = posts.count()
        paginator = Paginator(posts, 9)
        page_number = request.GET.get('page')
        paginated_posts = paginator.get_page(page_number)

        tags = Tag.objects.all()
        latest_posts = Post.objects.all().order_by('-id')[:3]

        return render(request, 'blog/category_template.html', {
            'category': category,
            'posts': paginated_posts,
            'tags': tags,
            'latest_posts': latest_posts,
            'all_categories': all_categories,
            'category_count': category_count,
        })
    except Category.DoesNotExist:
        messages.warning(request, "The selected category does not exist.")
        return redirect('blog')


def BlogTagView(request, slug):
    try:
        tag = get_object_or_404(Tag, slug=slug)
        all_categories = Category.objects.all()
        posts = Post.objects.filter(tags=tag).order_by('-id')
        tag_count = posts.count()
        paginator = Paginator(posts, 9)
        page_number = request.GET.get('page')
        paginated_posts = paginator.get_page(page_number)

        tags = Tag.objects.all()
        latest_posts = Post.objects.all().order_by('-id')[:3]

        return render(request, 'blog/tag_template.html', {
            'tag': tag,
            'posts': paginated_posts,
            'tags': tags,
            'latest_posts': latest_posts,
            'all_categories': all_categories,
            'tag_count': tag_count
        })
    except Tag.DoesNotExist:
        messages.warning(request, "The selected tag does not exist.")
        return redirect('blog')


def BlogSearchView(request):
    posts = Post.objects.all()
    tags = Tag.objects.all()
    category = Category.objects.all()
    latest_posts = Post.objects.all().order_by('-id')[:3]

    search_key = request.GET.get('s', '')

    # Redirect to shop if the search is empty
    if search_key == '':
        messages.warning(request, "Please enter a search term.")
        return redirect('blog')

    # Perform the search
    searched = Post.objects.filter(
        Q(title__icontains=search_key) |
        Q(category__name__icontains=search_key) |
        Q(tags__name__icontains=search_key)
    ).distinct()

    # Redirect if no products were found
    if not searched.exists():
        messages.warning(
            request, "That product doesn't exist. Please try again.")
        return redirect('blog')

    # Create the paginator
    paginator = Paginator(searched, 9)  # Show 9 products per page
    page = request.GET.get('page')

    try:
        paginated_results = paginator.page(page)
    except PageNotAnInteger:
        paginated_results = paginator.page(1)
    except EmptyPage:
        paginated_results = paginator.page(paginator.num_pages)

    return render(request, "blog/blog_search_template.html", {
        'search_key': search_key,
        'searched': paginated_results,  # Renamed here
        'posts': posts,
        'latest_posts': latest_posts,
        'tags': tags,
        'paginator': paginator,
        'category': category,
    })
