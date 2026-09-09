"""Models for the news application, including custom user model with role-based system."""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with a role-based system
    (Reader, Editor, Journalist)."""

    class Role(models.TextChoices):
        READER = "READER", "Reader"
        EDITOR = "EDITOR", "Editor"
        JOURNALIST = "JOURNALIST", "Journalist"

    role = models.CharField(max_length=20, choices=Role.choices)

    # Reader-only fields (per the ER diagram: Reader-Publisher and
    # Reader-Journalist)
    subscribed_publishers = models.ManyToManyField(
        "Publisher", related_name="subscribers", blank=True
    )
    subscribed_journalists = models.ManyToManyField(
        "self", symmetrical=False, related_name="followers", blank=True
    )

    def save(self, *args, **kwargs):
        """Save the user, then clear subscription fields if the role isn't
        Reader."""
        super().save(*args, **kwargs)
        if self.role != self.Role.READER:
            self.subscribed_publishers.clear()
            self.subscribed_journalists.clear()


class Publisher(models.Model):
    """A publishing organization that groups editors and journalists."""

    name = models.CharField(max_length=255)
    editors = models.ManyToManyField(User, related_name="edited_publishers", blank=True)
    journalists = models.ManyToManyField(
        User, related_name="journalist_publishers", blank=True
    )

    def __str__(self):
        return self.name


class Article(models.Model):
    """A news article written by a journalist, optionally tied to a
    publisher."""

    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="articles")
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Newsletter(models.Model):
    """A curated collection of articles, created by a journalist or editor."""

    title = models.CharField(max_length=255)
    description = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="newsletters"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    articles = models.ManyToManyField(Article, related_name="newsletters", blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
