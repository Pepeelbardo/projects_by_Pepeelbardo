"""Views implementing CRUD functionality for sticky notes."""

from django.shortcuts import render, get_object_or_404, redirect

from .forms import NoteForm
from .models import Note


def note_list(request):
    """Display all notes.

    :param request: HTTP request object.
    :return: Rendered template with the list of notes.
    """
    notes = Note.objects.all()
    context = {"notes": notes, "page_title": "All Notes"}
    return render(request, "notes/note_list.html", context)


def note_detail(request, pk):
    """Display a single note.

    :param request: HTTP request object.
    :param pk: Primary key of the note.
    :return: Rendered template with the note details.
    """
    note = get_object_or_404(Note, pk=pk)
    return render(request, "notes/note_detail.html", {"note": note})


def note_create(request):
    """Create a new note.

    :param request: HTTP request object.
    :return: Redirect on success, otherwise the rendered form.
    """
    if request.method == "POST":
        form = NoteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("note_list")
    else:
        form = NoteForm()
    return render(request, "notes/note_form.html", {"form": form})


def note_update(request, pk):
    """Update an existing note.

    :param request: HTTP request object.
    :param pk: Primary key of the note to update.
    :return: Redirect on success, otherwise the pre-filled form.
    """
    note = get_object_or_404(Note, pk=pk)
    if request.method == "POST":
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            return redirect("note_list")
    else:
        form = NoteForm(instance=note)
    return render(request, "notes/note_form.html", {"form": form})


def note_delete(request, pk):
    """Delete a note after confirmation.

    :param request: HTTP request object.
    :param pk: Primary key of the note to delete.
    :return: Redirect to the note list, or a confirmation page.
    """
    note = get_object_or_404(Note, pk=pk)
    if request.method == "POST":
        note.delete()
        return redirect("note_list")
    return render(request, "notes/note_confirm_delete.html", {"note": note})
