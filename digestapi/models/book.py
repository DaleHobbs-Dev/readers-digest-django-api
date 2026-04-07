"""Model for Book"""

from django.db import models
from django.contrib.auth.models import User


class Book(models.Model):
    """Represents a book created by a user in the Readers Digest application."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="books_created"
    )
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)

    # ISBN number can be stored as Null inside the database if it is not provided
    # ISBN number is optional and can be left blank when creating a book
    isbn = models.CharField(max_length=13, null=True, blank=True)
    cover_image_url = models.URLField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField(
        "Category", through="BookCategory", related_name="books"
    )
