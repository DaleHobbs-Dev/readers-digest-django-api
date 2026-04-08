"""Model for BookReview"""

from django.db import models
from django.contrib.auth.models import User
from .book import Book


class BookReview(models.Model):
    """Represents a review of a book created by a user in the Readers Digest application."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="book_reviews"
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField()
    review = models.TextField(blank=True)
    date_posted = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
