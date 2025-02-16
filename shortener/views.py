from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from django.views import View
from .models import ShortenedURL
from django import forms

# فرم برای ورودی لینک
class URLShortenerForm(forms.Form):
    url = forms.URLField(label='Enter URL', required=True)

# ویو برای ایجاد لینک کوتاه‌شده
class ShortenURLView(View):
    def get(self, request):
        form = URLShortenerForm()
        return render(request, 'shortener_form.html', {'form': form})
    
    def post(self, request):
        form = URLShortenerForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            shortened, created = ShortenedURL.objects.get_or_create(original_url=url)
            return render(request, 'shortener_form.html', {'form': form, 'short_url': request.build_absolute_uri(f'/{shortened.short_code}'), 'click_count': shortened.click_count})
        return render(request, 'shortener_form.html', {'form': form})

# ویو برای ریدایرکت و افزایش تعداد کلیک
class RedirectURLView(View):
    def get(self, request, code):
        url_entry = get_object_or_404(ShortenedURL, short_code=code)
        url_entry.click_count += 1
        url_entry.save()
        return redirect(url_entry.original_url)

# ویو برای نمایش آنالیتیکس تعداد کلیک‌ها
class AnalyticsView(View):
    def get(self, request, code):
        url_entry = get_object_or_404(ShortenedURL, short_code=code)
        return JsonResponse({'short_url': request.build_absolute_uri(f'/{code}'), 'click_count': url_entry.click_count})

