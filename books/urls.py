from django.urls import path

from .views import BooksListView, BooksDetailView, BookCheckoutView, add_to_cart, cart_detail, cart_item_delete, cart_item_update, create_book, delete_book, paymentComplete, SearchResultsListView, update_book
from .views import CategoryListView 
urlpatterns = [
    path('', BooksListView.as_view(), name='list'),
    path('<int:pk>/', BooksDetailView.as_view(), name='detail'),
    path('<int:pk>/checkout/', BookCheckoutView.as_view(), name='checkout'),
    path('cart/checkout/', BookCheckoutView.as_view(), name='cart_checkout'),
    path('complete/', paymentComplete, name='complete'),
    path('search/', SearchResultsListView.as_view(), name='search_results'),
    path('create_book/', create_book, name='create_book'),
    path('update/<int:pk>/', update_book, name='update_book'),
    path('delete/<int:pk>/', delete_book, name='delete_book'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('add-to-cart/<int:book_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', cart_detail, name='cart_detail'),
    path('update-item/<int:item_id>/', cart_item_update, name='cart_item_update'),
    path('cart/delete/<int:item_id>/', cart_item_delete, name='cart_item_delete'),
    
]
