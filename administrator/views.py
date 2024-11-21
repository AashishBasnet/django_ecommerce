from django.shortcuts import render, redirect
from Home.models import Product
from .forms import AddProductForm
from django.contrib import messages


def AddProductView(request):
    if request.method == "POST":
        # Include request.FILES for file uploads
        form = AddProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()  # Save the form data to the database
            return redirect('home')  # Replace with your success URL
        else:
            # Add a warning message if the form is not valid
            messages.warning(
                request, 'Please check the form for errors and try again.')
    else:
        form = AddProductForm()
    return render(request, "administrator/add_product_template.html", {"form": form})
