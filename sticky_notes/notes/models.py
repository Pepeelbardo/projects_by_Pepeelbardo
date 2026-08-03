"""Models for the sticky notes application."""

from django.db import models


class Note(models.Model):
    """Model representing a single sticky note.

    Fields:
        - title: CharField for the note title (max 200 characters).
        - content: TextField for the body of the note.
        - created_at: DateTimeField set automatically on creation.

    Methods:
        - __str__: Returns the note title.
    """

    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
