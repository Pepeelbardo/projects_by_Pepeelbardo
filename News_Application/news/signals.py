"""Signal handlers for the news app."""

import requests
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.core.mail import send_mail
from django.db.models.signals import post_migrate, post_save, pre_save
from django.dispatch import receiver

from .models import Article

ROLE_PERMISSIONS = {
    "Reader": {
        "Article": ["view"],
        "Newsletter": ["view"],
    },
    "Editor": {
        "Article": ["view", "change", "delete"],
        "Newsletter": ["view", "change", "delete"],
    },
    "Journalist": {
        "Article": ["add", "view", "change", "delete"],
        "Newsletter": ["add", "view", "change", "delete"],
    },
}

ROLE_TO_GROUP = {
    "READER": "Reader",
    "EDITOR": "Editor",
    "JOURNALIST": "Journalist",
}


@receiver(post_migrate)
def create_role_groups(sender, **kwargs):
    """Create the Reader, Editor and Journalist groups with their permissions."""
    if sender.name != "news":
        return

    for group_name, model_permissions in ROLE_PERMISSIONS.items():
        group, _ = Group.objects.get_or_create(name=group_name)
        permissions = []
        for model_name, actions in model_permissions.items():
            for action in actions:
                codename = f"{action}_{model_name.lower()}"
                try:
                    permissions.append(Permission.objects.get(codename=codename))
                except Permission.DoesNotExist:
                    pass
        group.permissions.set(permissions)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def assign_user_to_role_group(sender, instance, **kwargs):
    """Keep the user's group membership in sync with their role field."""
    target_group_name = ROLE_TO_GROUP.get(instance.role)

    for group_name in ROLE_TO_GROUP.values():
        group = Group.objects.get(name=group_name)
        if group_name == target_group_name:
            instance.groups.add(group)
        else:
            instance.groups.remove(group)


@receiver(pre_save, sender=Article)
def stash_previous_approval_state(sender, instance, **kwargs):
    """Remember whether the article was approved before this save."""
    if instance.pk:
        previous = (
            Article.objects.filter(pk=instance.pk)
            .values_list("approved", flat=True)
            .first()
        )
        instance._was_approved = bool(previous)
    else:
        instance._was_approved = False


@receiver(post_save, sender=Article)
def notify_on_approval(sender, instance, created, **kwargs):
    """Email subscribers and log the article to the internal API once it's approved."""
    if created:
        return  # A brand-new article isn't "approved by an editor" — it's just seed data.

    just_approved = instance.approved and not getattr(instance, "_was_approved", False)
    if not just_approved:
        return

    subscribers = set(instance.author.followers.all())
    if instance.publisher:
        subscribers.update(instance.publisher.subscribers.all())

    recipient_emails = [user.email for user in subscribers if user.email]
    if recipient_emails:
        try:
            send_mail(
                subject=f"New article: {instance.title}",
                message=f'{instance.author.username} just published "{instance.title}".',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_emails,
            )
        except OSError:
            pass  # Don't let an email delivery problem break the approval flow

    try:
        requests.post(
            f"{settings.SITE_BASE_URL}/api/approved/",
            json={"article_id": instance.id, "title": instance.title},
            timeout=5,
        )
    except requests.exceptions.RequestException as exc:
        print(f"[approved] Failed to reach /api/approved/: {exc}")
