from django.shortcuts import redirect, render
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Book, Order, Category
from django.db.models import Q
from django.http import JsonResponse
import json
from django.contrib.auth.decorators import login_required, user_passes_test

class BooksListView(ListView):
    model = Book
    template_name = 'list.html'

class BooksDetailView(DetailView):
    model = Book
    template_name = 'detail.html'

class SearchResultsListView(ListView):
    model = Book
    template_name = 'search_results.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        return Book.objects.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        )

def is_admin(user):
    return user.is_authenticated and user.is_superuser

@login_required
@user_passes_test(is_admin)
def create_book(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        category_id = request.POST.get('category', '')
        description = request.POST.get('description', '')
        price = request.POST.get('price', 0.0)
        image_url = request.POST.get('image_url', '')
        follow_author = request.POST.get('follow_author', '')
        book_available = request.POST.get('book_available', 0)

        # Récupérer l'objet Category correspondant à l'ID
        category = Category.objects.get(pk=category_id)

        book = Book(
            title=title,
            author=author,
            category=category,  # Utiliser l'objet Category
            description=description,
            price=price,
            image_url=image_url,
            follow_author=follow_author,
            book_available=book_available,
        )
        book.save()
        return redirect('list')

    return render(request, 'create_book.html', {'categories': categories})

class BookCheckoutView(LoginRequiredMixin, DetailView):
    model = Book
    template_name = 'checkout.html'
    login_url = 'login'

def paymentComplete(request):
    body = json.loads(request.body)
    print('BODY:', body)
    product = Book.objects.get(id=body['productId'])
    Order.objects.create(
        product=product
    )
    return JsonResponse('Payment completed!', safe=False)
