"""API views for the news app (Django REST Framework)."""

from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Article
from .permissions import ArticlePermission
from .serializers import ArticleSerializer


class ArticleViewSet(viewsets.ModelViewSet):
    """CRUD endpoints for articles, plus a 'subscribed' listing for readers."""

    serializer_class = ArticleSerializer
    permission_classes = [ArticlePermission]

    def get_queryset(self):
        """Approved-only for the public list; editors see everything;
        an authenticated user can also access their own pending articles."""
        user = self.request.user
        if self.action == "list":
            return Article.objects.filter(approved=True)
        if user.is_authenticated and user.groups.filter(name="Editor").exists():
            return Article.objects.all()
        if user.is_authenticated:
            return Article.objects.filter(Q(approved=True) | Q(author=user))
        return Article.objects.filter(approved=True)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False, methods=["get"])
    def subscribed(self, request):
        """Return approved articles from the reader's subscribed publishers/
        journalists."""
        user = request.user
        queryset = (
            Article.objects.filter(approved=True)
            .filter(
                Q(author__in=user.subscribed_journalists.all())
                | Q(publisher__in=user.subscribed_publishers.all())
            )
            .distinct()
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ApprovedArticleLogView(APIView):
    """Receives a POST when an article gets approved (simulates an external
    log)."""

    permission_classes = [AllowAny]

    def post(self, request):
        print(f"[approved] article_id={request.data.get('article_id')} title={
            request.data.get('title')
            }")
        return Response(status=201)
