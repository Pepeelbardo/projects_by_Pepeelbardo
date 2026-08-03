"""Forms for the sticky notes application."""

from django import forms

from .models import Note


class NoteForm(forms.ModelForm):
    """Form for creating and updating Note objects.

    Meta class:
        - model: Note
        - fields: title and content.
    """

    class Meta:
        model = Note
        fields = ["title", "content"]
