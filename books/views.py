from pyexpat.errors import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Book, Cart, CartItem, Order, Category
from django.db.models import Q
from django.http import JsonResponse
import json
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import UpdateView


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'category_detail.html'
    context_object_name = 'category'

class CategoryListView(ListView):
    model = Category
    template_name = 'category_list.html'
    context_object_name = 'categories' 

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
        query = self.request.GET.get('q', '')  # Default to empty string if not provided
        category_id = self.request.GET.get('category_id', '')  # Ensure this matches the name in your form

        queryset = Book.objects.all()  # Start with all books

        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(author__icontains=query))

        if category_id and category_id.isdigit():  # Ensure category_id is a valid number
            queryset = queryset.filter(category__id=category_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super(SearchResultsListView, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.all()  # Include all categories in context for dropdown
        return context



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

class BookCheckoutView(LoginRequiredMixin, View):
    login_url = 'login'
    template_name = 'checkout.html'

    def post(self, request):
        # Retrieve IDs from POST request (the selected cart items)
        selected_items = request.POST.getlist('selected_items')

        if not selected_items:
            messages.error(request, "No items selected for checkout.")
            return redirect('cart_detail')
        
        # Fetch the CartItems
        cart_items = CartItem.objects.filter(id__in=selected_items, cart__user=request.user)

        # Calculate the total cost or prepare data for payment processing
        total = sum(item.book.price * item.quantity for item in cart_items)

        # Check if there are items to checkout
        if not cart_items:
            messages.error(request, "Selected items are not available in your cart.")
            return redirect('cart_detail')
        
        # Context for the template
        context = {
            'cart_items': cart_items,
            'total_amount': total,  # Ensuring consistency with the template expecting `total_amount`
        }

        # Here you would typically handle payment logic, for now we just render a confirmation page
        return render(request, self.template_name, context)

    def get(self, request):
        # Redirect or display a message if accessed via GET
        messages.error(request, "Checkout page can only be accessed through cart selection.")
        return redirect('cart_detail')



def paymentComplete(request):
    body = json.loads(request.body)
    print('BODY:', body)
    product = Book.objects.get(id=body['productId'])
    Order.objects.create(
        product=product
    )
    return JsonResponse('Payment completed!', safe=False)

def cart_detail(request):
    try:
        cart = Cart.objects.get(user=request.user)  # assuming user is logged in
        items = cart.items.all()
    except Cart.DoesNotExist:
        items = []
    return render(request, 'cart/cart_detail.html', {'cart_items': items})

def cart_item_update(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    quantity = request.POST.get('quantity', 1)
    if int(quantity) <= 0:
        cart_item.delete()  # Remove item if quantity less than or equal to 0
    else:
        cart_item.quantity = int(quantity)
        cart_item.save()
    return redirect('cart_detail')

@login_required
def cart_item_delete(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)  # Ensures the item belongs to the user's cart
    cart_item.delete()
    return redirect('cart_detail')

@login_required
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    cart, created = Cart.objects.get_or_create(user=request.user, defaults={'user': request.user})

    # Vérifie si le livre est déjà dans le panier
    cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book, defaults={'cart': cart, 'book': book})

    if not created:
        # Si l'objet CartItem existait déjà, augmentez la quantité
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart_detail')