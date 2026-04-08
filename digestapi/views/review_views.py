"""Views for handling review-related API endpoints"""

from rest_framework import viewsets, status, serializers, permissions
from rest_framework.response import Response
from digestapi.models import BookReview


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for the Review model.

    Adds a computed `is_owner` field to indicate whether the requesting
    user is the author of the review.
    """

    is_owner = serializers.SerializerMethodField()

    def get_is_owner(self, obj):
        # Check if the user is the owner of the review
        return self.context["request"].user == obj.user

    class Meta:
        model = BookReview
        fields = ["id", "book", "user", "rating", "review", "date_posted", "is_owner"]
        read_only_fields = ["user"]


class ReviewViewSet(viewsets.ViewSet):
    # IsAuthenticated ensures only logged-in users can interact with reviews.
    # "Any user can leave a review" means any *authenticated* user, not the public.
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        # Get all reviews
        reviews = BookReview.objects.all()

        # Serialize the objects, and pass request to determine owner
        serializer = ReviewSerializer(reviews, many=True, context={"request": request})

        # Return the serialized data with 200 status code
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        """Create a new review instance from the request payload and save it to the database."""

        try:
            # Create a new instance of a review and assign property values from the request payload using `request.data`
            review = BookReview(
                user=request.user,
                book_id=request.data.get("book"),
                rating=request.data.get("rating"),
                review=request.data.get("review"),
            )

            # Save the review — this is the DB INSERT and can raise exceptions
            # (e.g. IntegrityError if book_id does not exist), so it must be
            # inside the try block.
            review.save()

            # Serialize the objects, and pass request as context
            serializer = ReviewSerializer(review, context={"request": request})

            # Return the serialized data with 201 status code
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Retrieve a single review by its primary key (pk)."""

        try:
            # Get the requested review
            review = BookReview.objects.get(pk=pk)
            # Serialize the object (make sure to pass the request as context)
            serializer = ReviewSerializer(review, context={"request": request})

            # Return the review with 200 status code
            return Response(serializer.data, status=status.HTTP_200_OK)

        except BookReview.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        """Delete a single review by its primary key (pk).

        This method first attempts to retrieve the review by its primary key.
        If the review exists, it checks whether the requesting user is the
        author of the review. If not, it returns a 403 Forbidden response.
        If the user is the author, the review is deleted and a 204 No Content
        response is returned. If the review does not exist, a 404 Not Found
        response is returned.
        """

        try:
            # Get the requested review
            review = BookReview.objects.get(pk=pk)

            # Check if the user has permission to delete
            # Will return 403 if authenticated user is not author
            if review.user.id != request.user.id:
                return Response(status=status.HTTP_403_FORBIDDEN)

            # Delete the review
            review.delete()

            # Return success but no body
            return Response(status=status.HTTP_204_NO_CONTENT)

        except BookReview.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
