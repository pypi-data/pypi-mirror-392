"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django import forms

# Define the form inline
class ContactForm(forms.Form):
    name = forms.CharField(label="Name", max_length=100, required=True)
    email = forms.EmailField(label="Email", required=True)
    message = forms.CharField(label="Message", widget=forms.Textarea, required=True)

# Views inline
def index_view(request):
    form = ContactForm()
    return render(request, "index.html", {"form": form})

def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            # Access cleaned data
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            message = form.cleaned_data["message"]

            # Handle the data (save, send email, etc.)
            messages.success(request, "Message sent successfully!")
            return redirect("contact")
    else:
        form = ContactForm()
    return render(request, "index.html", {"form": form})

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", index_view, name="index"),
    path("contact/", contact_view, name="contact"),
]
