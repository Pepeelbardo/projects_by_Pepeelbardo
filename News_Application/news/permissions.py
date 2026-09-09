"""Custom DRF permission classes based on the user's role/group."""

from rest_framework.permissions import SAFE_METHODS, BasePermission


class ArticlePermission(BasePermission):
    """
    Readers: read-only.
    Journalists: read, create, update, delete.
    Editors: read, update, delete (no create).
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        if request.method == "POST":
            return request.user.groups.filter(name="Journalist").exists()
        return request.user.groups.filter(name__in=["Journalist", "Editor"]).exists()
