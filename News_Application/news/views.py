"""Views for the news app."""

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import ArticleForm, EmailUpdateForm, NewsletterForm, SignUpForm
from .models import Article, Newsletter, Publisher, User


class EditorRequiredMixin(UserPassesTestMixin):
    """Restrict a view to users in the Editor group."""

    def test_func(self):
        return self.request.user.groups.filter(name="Editor").exists()


class PendingArticleListView(LoginRequiredMixin, EditorRequiredMixin, ListView):
    """List articles awaiting approval, visible only to editors."""

    model = Article
    template_name = "news/pending_articles.html"
    context_object_name = "articles"

    def get_queryset(self):
        return Article.objects.filter(approved=False)


def approve_article(request, pk):
    """Mark an article as approved. Only accessible to editors."""
    if not request.user.groups.filter(name="Editor").exists():
        return redirect("pending-articles")

    article = get_object_or_404(Article, pk=pk)
    article.approved = True
    article.save()
    return redirect("pending-articles")


class HomeView(ListView):
    """Public homepage listing approved articles, with the most recent one featured."""

    model = Article
    template_name = "news/home.html"
    context_object_name = "articles"

    def get_queryset(self):
        queryset = Article.objects.filter(approved=True)
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(title__icontains=query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "").strip()
        context["search_query"] = query
        articles = context["articles"]
        if query:
            context["featured_article"] = None
            context["other_articles"] = articles
        else:
            context["featured_article"] = articles.first()
            context["other_articles"] = articles[1:]
        return context


class SignUpView(CreateView):
    """Public registration. Logs the user in immediately after creating the account."""

    form_class = SignUpForm
    template_name = "news/signup.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class DiscoverView(LoginRequiredMixin, ListView):
    """Browse all approved articles, with search and the option to follow their authors."""

    model = Article
    template_name = "news/discover.html"
    context_object_name = "articles"

    def get_queryset(self):
        queryset = Article.objects.filter(approved=True)
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(title__icontains=query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["following_ids"] = set(
            self.request.user.subscribed_journalists.values_list("id", flat=True)
        )
        context["following_publisher_ids"] = set(
            self.request.user.subscribed_publishers.values_list("id", flat=True)
        )
        context["search_query"] = self.request.GET.get("q", "")
        return context


class FollowingView(LoginRequiredMixin, ListView):
    """Articles from the journalists/publishers the current reader follows."""

    template_name = "news/following.html"
    context_object_name = "articles"

    def get_queryset(self):
        user = self.request.user
        return (
            Article.objects.filter(approved=True)
            .filter(
                Q(author__in=user.subscribed_journalists.all())
                | Q(publisher__in=user.subscribed_publishers.all())
            )
            .distinct()
        )


class AccountView(LoginRequiredMixin, UpdateView):
    """Show account info and let the user update their email."""

    model = User
    form_class = EmailUpdateForm
    template_name = "news/account.html"
    success_url = reverse_lazy("account")

    def get_object(self, queryset=None):
        return self.request.user


@login_required
def toggle_follow_journalist(request, user_id):
    """Follow or unfollow a journalist, then return to the page the user came from."""
    journalist = get_object_or_404(User, pk=user_id, role=User.Role.JOURNALIST)
    if journalist in request.user.subscribed_journalists.all():
        request.user.subscribed_journalists.remove(journalist)
    else:
        request.user.subscribed_journalists.add(journalist)
    return redirect(request.META.get("HTTP_REFERER", "discover"))


@login_required
def toggle_follow_publisher(request, publisher_id):
    """Follow or unfollow a publisher, then return to the page the user came from."""
    publisher = get_object_or_404(Publisher, pk=publisher_id)
    if publisher in request.user.subscribed_publishers.all():
        request.user.subscribed_publishers.remove(publisher)
    else:
        request.user.subscribed_publishers.add(publisher)
    return redirect(request.META.get("HTTP_REFERER", "discover"))


class ArticleDetailView(DetailView):
    """Detail page for an article. Approved articles are public; an unapproved
    article is visible only to its own author or to an editor."""

    model = Article
    template_name = "news/article_detail.html"
    context_object_name = "article"

    def get_queryset(self):
        queryset = Article.objects.all()
        user = self.request.user
        if user.is_authenticated and user.groups.filter(name="Editor").exists():
            return queryset
        if user.is_authenticated:
            return queryset.filter(Q(approved=True) | Q(author=user))
        return queryset.filter(approved=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["is_following_author"] = (
                self.object.author in self.request.user.subscribed_journalists.all()
            )
            if self.object.publisher:
                context["is_following_publisher"] = (
                    self.object.publisher
                    in self.request.user.subscribed_publishers.all()
                )
        return context


class JournalistRequiredMixin(UserPassesTestMixin):
    """Restrict a view to users in the Journalist group."""

    def test_func(self):
        return self.request.user.groups.filter(name="Journalist").exists()


class ArticleCreateView(LoginRequiredMixin, JournalistRequiredMixin, CreateView):
    """Let a journalist submit a new article for editor review."""

    model = Article
    form_class = ArticleForm
    template_name = "news/article_form.html"
    success_url = reverse_lazy("my-articles")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class MyArticlesView(LoginRequiredMixin, JournalistRequiredMixin, ListView):
    """List of the current journalist's own articles, with approval status."""

    template_name = "news/my_articles.html"
    context_object_name = "articles"

    def get_queryset(self):
        return self.request.user.articles.all()


class NewsletterCreateView(LoginRequiredMixin, CreateView):
    """Let a journalist or editor create a newsletter from approved articles."""

    model = Newsletter
    form_class = NewsletterForm
    template_name = "news/newsletter_form.html"
    success_url = reverse_lazy("home")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name__in=["Journalist", "Editor"]).exists():
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class ManageArticlesView(LoginRequiredMixin, EditorRequiredMixin, ListView):
    """List every article, regardless of status, for an editor to manage."""

    model = Article
    template_name = "news/manage_articles.html"
    context_object_name = "articles"

    def get_queryset(self):
        return Article.objects.all()


class ArticleUpdateView(LoginRequiredMixin, EditorRequiredMixin, UpdateView):
    """Let an editor correct any article's title, content, or publisher."""

    model = Article
    fields = ["title", "content", "publisher"]
    template_name = "news/article_form.html"
    success_url = reverse_lazy("manage-articles")


class ArticleDeleteView(LoginRequiredMixin, EditorRequiredMixin, DeleteView):
    """Let an editor delete an article."""

    model = Article
    template_name = "news/article_confirm_delete.html"
    success_url = reverse_lazy("manage-articles")


class NewsletterListView(ListView):
    """Public list of all newsletters."""

    model = Newsletter
    template_name = "news/newsletter_list.html"
    context_object_name = "newsletters"


class NewsletterDetailView(DetailView):
    """Public detail page for a newsletter and its included articles."""

    model = Newsletter
    template_name = "news/newsletter_detail.html"
    context_object_name = "newsletter"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["is_following_author"] = (
                self.object.author in self.request.user.subscribed_journalists.all()
            )
        return context


class NewsletterUpdateView(LoginRequiredMixin, UpdateView):
    """Edit a newsletter. Journalists may only edit their own; editors may edit any."""

    model = Newsletter
    form_class = NewsletterForm
    template_name = "news/newsletter_form.html"
    success_url = reverse_lazy("newsletter-list")

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Editor").exists():
            return Newsletter.objects.all()
        return Newsletter.objects.filter(author=user)


class NewsletterDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a newsletter. Journalists may only delete their own; editors may delete any."""

    model = Newsletter
    template_name = "news/newsletter_confirm_delete.html"
    success_url = reverse_lazy("newsletter-list")

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Editor").exists():
            return Newsletter.objects.all()
        return Newsletter.objects.filter(author=user)


class MyNewslettersView(LoginRequiredMixin, JournalistRequiredMixin, ListView):
    """List of the current journalist's own newsletters."""

    template_name = "news/my_newsletters.html"
    context_object_name = "newsletters"

    def get_queryset(self):
        return self.request.user.newsletters.all()


class ManageNewslettersView(LoginRequiredMixin, EditorRequiredMixin, ListView):
    """List every newsletter for an editor to manage."""

    model = Newsletter
    template_name = "news/manage_newsletters.html"
    context_object_name = "newsletters"
