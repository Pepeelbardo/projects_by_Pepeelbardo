"""Serializers for the news app's REST API."""

from rest_framework import serializers

from .models import Article, Newsletter, Publisher, User


class PublisherSerializer(serializers.ModelSerializer):
    """This serializer is used to represent the Publisher model in the API."""

    class Meta:
        model = Publisher
        fields = ["id", "name"]


class UserSerializer(serializers.ModelSerializer):
    """Represents the User model in the API, including the user's role."""

    class Meta:
        model = User
        fields = ["id", "username", "email", "role"]


class ArticleSerializer(serializers.ModelSerializer):
    """Represents the Article model, including its author and publisher."""

    author = UserSerializer(read_only=True)

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "content",
            "author",
            "publisher",
            "created_at",
            "approved",
        ]
        read_only_fields = ["approved", "created_at"]


class NewsletterSerializer(serializers.ModelSerializer):
    """This serializer is used to represent the Newsletter model in the API,
    including the author and articles."""

    author = UserSerializer(read_only=True)

    class Meta:
        model = Newsletter
        fields = ["id", "title", "description", "author", "created_at", "articles"]
