from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

class ShortenedURL(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    original_url = models.URLField(unique=True)
    short_code = models.CharField(max_length=10, unique=True, blank=True)
    click_count = models.IntegerField(default=0)  # تعداد کلیک‌ها

    def save(self, *args, **kwargs):
        if not self.short_code:
            self.short_code = get_random_string(6)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.short_code} -> {self.original_url}"
