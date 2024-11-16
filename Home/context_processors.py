from .models import Categories


def categories(request):
    categories = Categories.objects.all().order_by('-id')[:6]
    return {
        'categories': categories
    }
