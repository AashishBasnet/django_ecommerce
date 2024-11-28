from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages


class SuperuserRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Exclude specific paths to avoid redirect loops
        excluded_paths = ['/login/', '/logout/',
                          '/register/', '/update-password/', '/admin/']

        if any(request.path.startswith(path) for path in excluded_paths):
            return self.get_response(request)

        # Apply middleware to `/administrator/` paths
        if request.path.startswith('/administrator/') and not (request.user.is_authenticated and request.user.is_superuser):
            # Redirect to 'login' in the Home app with the `next` parameter
            messages.warning(
                request, 'only authorized personnel are allowed on this page')
            return redirect(reverse('home') + f"?next={request.path}")

        return self.get_response(request)
