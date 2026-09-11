"""API URL routes for the news app (Django REST Framework)."""

from django.urls import path
from rest_framework.routers import DefaultRouter

from .api_views import ApprovedArticleLogView, ArticleViewSet

router = DefaultRouter()
router.register("articles", ArticleViewSet, basename="article")

urlpatterns = [
    path("approved/", ApprovedArticleLogView.as_view(), name="api-approved"),
] + router.urls
