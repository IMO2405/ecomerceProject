from django.urls import path

from .views import BooksListView, BooksDetailView, BookCheckoutView, create_book, delete_book, paymentComplete, SearchResultsListView, update_book

urlpatterns = [
    path('', BooksListView.as_view(), name='list'),
    path('<int:pk>/', BooksDetailView.as_view(), name='detail'),
    path('<int:pk>/checkout/', BookCheckoutView.as_view(), name='checkout'),
    path('complete/', paymentComplete, name='complete'),
    path('search/', SearchResultsListView.as_view(), name='search_results'),
    path('create_book/', create_book, name='create_book'),
    path('update/<int:pk>/', update_book, name='update_book'),
    path('delete/<int:pk>/', delete_book, name='delete_book'),
]
