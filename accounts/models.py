# accounts.models.py
from django.db import models
from django.contrib.auth.models import User
# Corrected import
from books.models import Book

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    new_password = models.CharField(max_length=128)
