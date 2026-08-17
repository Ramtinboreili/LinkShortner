"""Helpers for generating and validating short codes."""

import secrets
import string

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# Base62 minus look-alike characters, so codes stay readable when typed by hand
# or read off a QR code.
CODE_ALPHABET = "".join(
    c for c in string.ascii_letters + string.digits if c not in "0OIl1"
)

# Codes that would shadow a real route. `<code>` is matched at the URL root, so
# anything reachable under `/` must be excluded from generated and custom codes.
RESERVED_CODES = frozenset(
    {
        "admin",
        "api",
        "dashboard",
        "favicon.ico",
        "healthz",
        "login",
        "logout",
        "media",
        "qr",
        "register",
        "robots.txt",
        "static",
    }
)

MAX_CODE_LENGTH = 32
MIN_CODE_LENGTH = 3


def generate_short_code(length: int | None = None) -> str:
    """Return a cryptographically random code of the configured length."""
    length = length or settings.SHORT_CODE_LENGTH
    return "".join(secrets.choice(CODE_ALPHABET) for _ in range(length))


def generate_unique_short_code(model, length: int | None = None, attempts: int = 10) -> str:
    """Return a code that is not yet taken.

    Collisions are vanishingly unlikely at the default length, but a busy
    database will eventually see one; widen the code rather than fail.
    """
    length = length or settings.SHORT_CODE_LENGTH
    for attempt in range(attempts):
        code = generate_short_code(length + attempt // 5)
        if not model.objects.filter(short_code=code).exists():
            return code
    raise RuntimeError("Unable to generate a unique short code")


def validate_short_code(value: str) -> None:
    """Validate a user-supplied custom alias."""
    if len(value) < MIN_CODE_LENGTH:
        raise ValidationError(
            _("Custom alias must be at least %(min)d characters."),
            params={"min": MIN_CODE_LENGTH},
        )
    if len(value) > MAX_CODE_LENGTH:
        raise ValidationError(
            _("Custom alias must be at most %(max)d characters."),
            params={"max": MAX_CODE_LENGTH},
        )
    allowed = set(string.ascii_letters + string.digits + "-_")
    if not set(value) <= allowed:
        raise ValidationError(_("Custom alias may only contain letters, digits, - and _."))
    if value.lower() in RESERVED_CODES:
        raise ValidationError(_("That alias is reserved."))
