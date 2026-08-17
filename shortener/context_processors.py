from django.conf import settings


def site_settings(request):
    """Expose a few settings to every template."""
    return {
        "SITE_NAME": settings.SITE_NAME,
        "ALLOW_REGISTRATION": settings.ALLOW_REGISTRATION,
    }
