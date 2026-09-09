"""Automated tests for the news app."""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from django.core import mail
from .models import Newsletter
from .models import Article

User = get_user_model()


class ArticleAPITestCase(APITestCase):
    """Tests for the /api/articles/ endpoints, covering role-based permissions."""

    def setUp(self):
        self.journalist = User.objects.create_user(
            username="journalist", password="pass1234", role="JOURNALIST"
        )
        self.editor = User.objects.create_user(
            username="editor", password="pass1234", role="EDITOR"
        )
        self.reader = User.objects.create_user(
            username="reader", password="pass1234", role="READER"
        )
        self.reader.subscribed_journalists.add(self.journalist)

        self.approved_article = Article.objects.create(
            title="Approved Article",
            content="Content",
            author=self.journalist,
            approved=True,
        )
        self.pending_article = Article.objects.create(
            title="Pending Article",
            content="Content",
            author=self.journalist,
            approved=False,
        )

    def authenticate(self, user):
        """Log in as the given user and attach their token to the test client."""
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": user.username, "password": "pass1234"},
        )
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_unauthenticated_user_cannot_list_articles(self):
        response = self.client.get("/api/articles/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_only_returns_approved_articles(self):
        self.authenticate(self.reader)
        response = self.client.get("/api/articles/")
        titles = [article["title"] for article in response.data]
        self.assertIn("Approved Article", titles)
        self.assertNotIn("Pending Article", titles)

    def test_reader_cannot_create_article(self):
        self.authenticate(self.reader)
        response = self.client.post(
            "/api/articles/", {"title": "New", "content": "Content"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_journalist_can_create_article(self):
        self.authenticate(self.journalist)
        response = self.client.post(
            "/api/articles/", {"title": "New", "content": "Content"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["author"]["username"], "journalist")
        self.assertFalse(response.data["approved"])

    def test_journalist_cannot_self_approve_via_api(self):
        self.authenticate(self.journalist)
        response = self.client.post(
            "/api/articles/",
            {"title": "Sneaky", "content": "Content", "approved": True},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(response.data["approved"])

    def test_journalist_can_delete_own_article(self):
        self.authenticate(self.journalist)
        response = self.client.delete(f"/api/articles/{self.pending_article.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_editor_can_delete_article(self):
        self.authenticate(self.editor)
        response = self.client.delete(f"/api/articles/{self.approved_article.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_reader_cannot_delete_article(self):
        self.authenticate(self.reader)
        response = self.client.delete(f"/api/articles/{self.approved_article.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_journalist_can_update_own_article(self):
        self.authenticate(self.journalist)
        response = self.client.patch(
            f"/api/articles/{self.pending_article.id}/",
            {"title": "Updated Title"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated Title")

    def test_reader_cannot_update_article(self):
        self.authenticate(self.reader)
        response = self.client.patch(
            f"/api/articles/{self.approved_article.id}/",
            {"title": "Hacked Title"},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_subscribed_endpoint_returns_only_followed_authors(self):
        other_journalist = User.objects.create_user(
            username="other_journalist", password="pass1234", role="JOURNALIST"
        )
        Article.objects.create(
            title="Not Followed",
            content="Content",
            author=other_journalist,
            approved=True,
        )
        self.authenticate(self.reader)
        response = self.client.get("/api/articles/subscribed/")
        titles = [article["title"] for article in response.data]
        self.assertIn("Approved Article", titles)
        self.assertNotIn("Not Followed", titles)


class ArticleApprovalSignalTestCase(APITestCase):
    """Tests for the post-approval signal: email notification and /api/approved/ logging."""

    def setUp(self):
        self.journalist = User.objects.create_user(
            username="journalist2", password="pass1234", role="JOURNALIST"
        )
        self.reader = User.objects.create_user(
            username="reader2",
            password="pass1234",
            role="READER",
            email="reader2@example.com",
        )
        self.reader.subscribed_journalists.add(self.journalist)
        self.article = Article.objects.create(
            title="Pending Approval",
            content="Content",
            author=self.journalist,
            approved=False,
        )

    @patch("news.signals.requests.post")
    def test_approving_article_sends_email_to_subscribers(self, mock_post):
        self.article.approved = True
        self.article.save()

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("reader2@example.com", mail.outbox[0].to)
        self.assertIn("Pending Approval", mail.outbox[0].subject)

    @patch("news.signals.requests.post")
    def test_approving_article_posts_to_internal_api(self, mock_post):
        self.article.approved = True
        self.article.save()

        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        self.assertEqual(kwargs["json"]["article_id"], self.article.id)
        self.assertEqual(kwargs["json"]["title"], "Pending Approval")

    @patch("news.signals.requests.post")
    def test_editing_already_approved_article_does_not_resend_email(self, mock_post):
        self.article.approved = True
        self.article.save()
        mail.outbox.clear()
        mock_post.reset_mock()

        self.article.title = "Pending Approval (typo fixed)"
        self.article.save()

        self.assertEqual(len(mail.outbox), 0)
        mock_post.assert_not_called()

    @patch("news.signals.requests.post")
    def test_no_email_sent_when_author_has_no_subscribers(self, mock_post):
        lonely_journalist = User.objects.create_user(
            username="lonely", password="pass1234", role="JOURNALIST"
        )
        article = Article.objects.create(
            title="Nobody Follows Me",
            content="Content",
            author=lonely_journalist,
            approved=False,
        )
        article.approved = True
        article.save()

        self.assertEqual(len(mail.outbox), 0)
        mock_post.assert_called_once()


class NewsletterModelTestCase(TestCase):
    """Model-level tests for Newsletter."""

    def setUp(self):
        self.journalist = User.objects.create_user(
            username="journalist3", password="pass1234", role="JOURNALIST"
        )
        self.article = Article.objects.create(
            title="Included Article",
            content="Content",
            author=self.journalist,
            approved=True,
        )

    def test_newsletter_can_include_multiple_articles(self):
        newsletter = Newsletter.objects.create(
            title="Weekly Digest",
            description="This week in news.",
            author=self.journalist,
        )
        newsletter.articles.add(self.article)

        self.assertEqual(newsletter.articles.count(), 1)
        self.assertIn(self.article, newsletter.articles.all())

    def test_newsletter_str_returns_title(self):
        newsletter = Newsletter.objects.create(
            title="Weekly Digest",
            description="This week in news.",
            author=self.journalist,
        )
        self.assertEqual(str(newsletter), "Weekly Digest")
