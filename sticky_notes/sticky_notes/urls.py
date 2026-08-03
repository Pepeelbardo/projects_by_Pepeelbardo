"""Root URL configuration for the sticky_notes project."""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("notes.urls")),
]
