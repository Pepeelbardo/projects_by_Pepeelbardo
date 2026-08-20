from django.conf import settings
from django.db import models


class ResetToken(models.Model):
    """Stores a hashed, single-use password reset token with an
    expiry date for a user."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    token = models.CharField(max_length=255, unique=True)
    expiry_date = models.DateTimeField()
    used = models.BooleanField(default=False)

    def __str__(self):
        return (
            f"ResetToken(user={self.user.username}, "
            f"token={self.token[:10]}..., used={self.used})"
        )
