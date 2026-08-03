"""Unit tests for the notes application."""

from django.test import TestCase
from django.urls import reverse

from .models import Note


class NoteModelTests(TestCase):
    """Tests for the Note model."""

    def test_str_returns_title(self):
        """__str__ should return the note title."""
        note = Note.objects.create(title="Groceries", content="Milk and eggs")
        self.assertEqual(str(note), "Groceries")

    def test_created_at_is_set_automatically(self):
        """created_at should be populated on creation."""
        note = Note.objects.create(title="Reminder", content="Call the dentist")
        self.assertIsNotNone(note.created_at)

    def test_notes_are_ordered_newest_first(self):
        """Meta.ordering should return the most recent note first."""
        Note.objects.create(title="First", content="Oldest note")
        second = Note.objects.create(title="Second", content="Newest note")
        self.assertEqual(Note.objects.first(), second)


class NoteViewTests(TestCase):
    """Tests for the CRUD views."""

    def setUp(self):
        """Create a note shared by the view tests."""
        self.note = Note.objects.create(title="Shopping", content="Buy bread")

    def test_list_view_shows_existing_notes(self):
        """The list view should render existing note titles."""
        response = self.client.get(reverse("note_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Shopping")

    def test_detail_view_returns_404_for_missing_note(self):
        """Requesting a non-existent note should return 404, not 500."""
        response = self.client.get(reverse("note_detail", args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_detail_view_shows_note_content(self):
        """The detail view should render the note's title and content."""
        response = self.client.get(reverse('note_detail', args=[self.note.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.note.title)
        self.assertContains(response, self.note.content)

    def test_create_view_saves_new_note(self):
        """A valid POST should save the note and redirect to the list."""
        response = self.client.post(
            reverse("note_create"),
            {"title": "New note", "content": "Created from a test"},
        )
        self.assertRedirects(response, reverse("note_list"))
        self.assertTrue(Note.objects.filter(title="New note").exists())

    def test_update_view_prefills_form_with_existing_data(self):
        """A GET request should show the form filled with the current note's data."""
        response = self.client.get(reverse('note_update', args=[self.note.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.note.title)

    def test_create_view_rerenders_form_on_invalid_data(self):
        """An invalid POST (missing title) should re-render the form without saving."""
        response = self.client.post(
            reverse('note_create'),
            {'title': '', 'content': 'No title here'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Note.objects.filter(content='No title here').exists())

    def test_update_view_saves_changes_on_post(self):
        """A valid POST should update the existing note in place, not create a new one."""
        response = self.client.post(
            reverse('note_update', args=[self.note.pk]),
            {'title': 'Shopping (updated)', 'content': 'Buy bread and milk'},
        )
        self.assertRedirects(response, reverse('note_list'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Shopping (updated)')
        self.assertEqual(Note.objects.count(), 1)

    def test_delete_view_requires_post(self):
        """A GET should show the confirmation page without deleting."""
        response = self.client.get(reverse("note_delete", args=[self.note.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Note.objects.filter(pk=self.note.pk).exists())

    def test_delete_view_removes_note_on_post(self):
        """A POST should delete the note and redirect to the list."""
        response = self.client.post(reverse("note_delete", args=[self.note.pk]))
        self.assertRedirects(response, reverse("note_list"))
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())
