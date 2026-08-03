"""Admin registration for the notes app."""

from django.contrib import admin

from .models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    """Admin configuration for the Note model."""

    list_display = ("title", "created_at")
    search_fields = ("title", "content")
