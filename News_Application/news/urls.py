"""URL routes for the news app."""

from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy
from rest_framework.routers import DefaultRouter

from . import views
from .api_views import ApprovedArticleLogView, ArticleViewSet

router = DefaultRouter()
router.register("api/articles", ArticleViewSet, basename="article")

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(template_name="news/login.html"),
        name="login",
    ),
    path(
        "accounts/logout/",
        auth_views.LogoutView.as_view(next_page="home"),
        name="logout",
    ),
    path("accounts/signup/", views.SignUpView.as_view(), name="signup"),
    path(
        "editor/pending/",
        views.PendingArticleListView.as_view(),
        name="pending-articles",
    ),
    path("editor/approve/<int:pk>/", views.approve_article, name="approve-article"),
    path("api/approved/", ApprovedArticleLogView.as_view(), name="api-approved"),
    path("following/", views.FollowingView.as_view(), name="following"),
    path("discover/", views.DiscoverView.as_view(), name="discover"),
    path("account/", views.AccountView.as_view(), name="account"),
    path("follow/<int:user_id>/", views.toggle_follow_journalist, name="toggle-follow"),
    path(
        "follow/publisher/<int:publisher_id>/",
        views.toggle_follow_publisher,
        name="toggle-follow-publisher",
    ),
    path("articles/<int:pk>/", views.ArticleDetailView.as_view(), name="article-page"),
    path("articles/create/", views.ArticleCreateView.as_view(), name="article-create"),
    path("articles/mine/", views.MyArticlesView.as_view(), name="my-articles"),
    path(
        "newsletters/create/",
        views.NewsletterCreateView.as_view(),
        name="newsletter-create",
    ),
    path("editor/manage/", views.ManageArticlesView.as_view(), name="manage-articles"),
    path(
        "editor/articles/<int:pk>/edit/",
        views.ArticleUpdateView.as_view(),
        name="article-edit",
    ),
    path(
        "editor/articles/<int:pk>/delete/",
        views.ArticleDeleteView.as_view(),
        name="article-delete",
    ),
    path("newsletters/", views.NewsletterListView.as_view(), name="newsletter-list"),
    path(
        "newsletters/<int:pk>/",
        views.NewsletterDetailView.as_view(),
        name="newsletter-page",
    ),
    path("newsletters/mine/", views.MyNewslettersView.as_view(), name="my-newsletters"),
    path(
        "newsletters/<int:pk>/edit/",
        views.NewsletterUpdateView.as_view(),
        name="newsletter-edit",
    ),
    path(
        "newsletters/<int:pk>/delete/",
        views.NewsletterDeleteView.as_view(),
        name="newsletter-delete",
    ),
    path(
        "editor/newsletters/",
        views.ManageNewslettersView.as_view(),
        name="manage-newsletters",
    ),
    path(
        "account/password/",
        auth_views.PasswordChangeView.as_view(
            template_name="news/password_change.html",
            success_url=reverse_lazy("password-change-done"),
        ),
        name="password-change",
    ),
    path(
        "account/password/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="news/password_change_done.html",
        ),
        name="password-change-done",
    ),
    path(
        "editor/publishers/", views.PublisherListView.as_view(), name="publisher-list"
    ),
    path(
        "editor/publishers/create/",
        views.PublisherCreateView.as_view(),
        name="publisher-create",
    ),
    path(
        "editor/publishers/<int:pk>/edit/",
        views.PublisherUpdateView.as_view(),
        name="publisher-edit",
    ),
    path(
        "editor/publishers/<int:pk>/delete/",
        views.PublisherDeleteView.as_view(),
        name="publisher-delete",
    ),
] + router.urls
