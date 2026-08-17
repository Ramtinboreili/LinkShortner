from django.contrib import admin
from django.utils.html import format_html

from .models import ShortenedURL


@admin.register(ShortenedURL)
class ShortenedURLAdmin(admin.ModelAdmin):
    list_display = ("short_code", "destination", "user", "click_count", "created_at")
    list_filter = ("created_at", "user")
    search_fields = ("short_code", "original_url", "user__username")
    readonly_fields = ("click_count", "created_at", "last_clicked_at")
    list_select_related = ("user",)
    ordering = ("-created_at",)

    @admin.display(description="Destination", ordering="original_url")
    def destination(self, obj):
        return format_html(
            '<a href="{}" target="_blank" rel="noopener">{}</a>',
            obj.original_url,
            obj.original_url[:80] + ("…" if len(obj.original_url) > 80 else ""),
        )
