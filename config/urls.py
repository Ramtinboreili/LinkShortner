"""Root URL configuration.

The shortener app owns the root namespace because short codes live directly
under `/<code>`; its catch-all pattern must therefore be included last.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("shortener.urls")),
]
