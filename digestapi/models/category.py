"""Model for Category"""

from django.db import models


class Category(models.Model):
    """Represents a category that can be assigned to books in the Readers Digest application."""

    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
