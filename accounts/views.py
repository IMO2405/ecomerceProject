from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.views import generic
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from .models import Book

class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

@login_required
def profile_update(request):
    user = request.user
    if request.method == 'POST':
        password_form = PasswordChangeForm(user, request.POST)
        if password_form.is_valid():
            password_form.save()
            messages.success(request, 'Your password has been updated successfully.')
            return redirect('update')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        password_form = PasswordChangeForm(user)

    return render(request, 'profile_update.html', {'password_form': password_form})

def is_admin_user(user):
    return user.is_authenticated and user.is_superuser

@user_passes_test(is_admin_user)
def book_creation(request):
    if request.method == 'POST':
        title = request.POST.get('title', '')
        author = request.POST.get('author', '')
        description = request.POST.get('description', '')
        
        if title and author:  # Simple validation to ensure title and author are provided
            Book.objects.create(title=title, author=author, description=description)
            messages.success(request, 'Book created successfully.')
            return redirect('books_list')  # Make sure this redirect URL is correct
        else:
            messages.error(request, 'Title and author are required.')

    return render(request, 'your_app/book_creation.html')
