from django.contrib import admin
from .models import Book, Order,Category



admin.site.register(Book)
admin.site.register(Order)

admin.site.register(Category)