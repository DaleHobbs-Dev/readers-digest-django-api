"""Views for user registration and authentication in the Readers Digest application."""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model to handle registration and authentication."""

    class Meta:
        model = User
        fields = ["id", "username", "password", "first_name", "last_name"]
        extra_kwargs = {"password": {"write_only": True}}


class UserViewSet(viewsets.ViewSet):
    """ViewSet for handling user registration and authentication."""

    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=["post"], url_path="register")
    def register_account(self, request):
        """Handles user registration by creating a new user and returning an authentication token."""
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            data: dict = serializer.validated_data
            user = User.objects.create_user(
                username=data["username"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                password=data["password"],
            )
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="login")
    def user_login(self, request):
        """Handles user login by authenticating credentials and returning an authentication token."""
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if user:
            token = Token.objects.get(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST
            )
