from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Book, Order, Category
from django.db.models import Q
from django.http import JsonResponse
import json
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import UpdateView

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
        print(f"Recherche pour: {query}")  # Ajoutez cette ligne pour le débogage
        if query:
            result = Book.objects.filter(Q(title__icontains=query) | Q(author__icontains=query))
            print(f"Nombre de résultats trouvés: {result.count()}")  # Débogage
            return result
        return Book.objects.none()



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

@login_required
@user_passes_test(is_admin)
def update_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    categories = Category.objects.all()
    if request.method == 'POST':
        book.title = request.POST.get('title', book.title)
        book.author = request.POST.get('author', book.author)
        book.description = request.POST.get('description', book.description)
        book.price = request.POST.get('price', book.price)
        book.image_url = request.POST.get('image_url', book.image_url)
        book.follow_author = request.POST.get('follow_author', book.follow_author)
        book.book_available = request.POST.get('book_available', book.book_available)
        category_id = request.POST.get('category')
        if category_id:
            book.category = get_object_or_404(Category, pk=category_id)
        book.save()
        return redirect('detail', pk=book.pk)
    return render(request, 'update_book.html', {'book': book, 'categories': categories})

@login_required
@user_passes_test(is_admin)
def delete_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('list')  # Assurez-vous que 'list' est le nom correct de la vue qui affiche la liste des livres
    return redirect('list')

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
