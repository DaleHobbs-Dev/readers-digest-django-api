"""View Module for Handling Requests about Categories"""

from rest_framework import viewsets, status
from rest_framework import serializers
from rest_framework.response import Response
from digestapi.models import Category


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category Model"""

    class Meta:
        model = Category
        fields = ["id", "name"]


class CategoryViewSet(viewsets.ViewSet):
    """ViewSet for handling Category requests"""

    def list(self, request):
        """Handle GET requests to list all categories"""
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Handle GET requests for a single category by its ID"""

        try:
            category = Category.objects.get(pk=pk)
            serializer = CategorySerializer(category)
            return Response(serializer.data)
        except Category.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
