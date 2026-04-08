"""URL configuration for the Readers Digest application."""

from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from digestapi.views import UserViewSet, CategoryViewSet, BookViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"books", BookViewSet, basename="book")

urlpatterns = [
    path("", include(router.urls)),
    path("login", UserViewSet.as_view({"post": "user_login"}), name="login"),
    path(
        "register", UserViewSet.as_view({"post": "register_account"}), name="register"
    ),
    path("admin/", admin.site.urls),
]
