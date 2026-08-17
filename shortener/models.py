from django.conf import settings
from django.core.validators import URLValidator
from django.db import models
from django.urls import reverse

from .utils import MAX_CODE_LENGTH, generate_unique_short_code


class ShortenedURL(models.Model):
    """A single short link owned by a user."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="links",
        null=True,
        blank=True,
    )
    # Only http/https are accepted: the value is fed straight into a redirect,
    # so schemes such as javascript: or file: must never reach the browser.
    original_url = models.URLField(
        max_length=2048,
        validators=[URLValidator(schemes=["http", "https"])],
    )
    short_code = models.CharField(max_length=MAX_CODE_LENGTH, unique=True, db_index=True)
    click_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    last_clicked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("user", "-created_at"), name="shortener_user_created_idx")
        ]

    def __str__(self) -> str:
        return f"{self.short_code} -> {self.original_url}"

    def save(self, *args, **kwargs):
        if not self.short_code:
            self.short_code = generate_unique_short_code(type(self))
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("redirect_url", kwargs={"code": self.short_code})

    def build_short_url(self, request) -> str:
        """Absolute short URL, honouring the host the request came in on."""
        return request.build_absolute_uri(self.get_absolute_url())
