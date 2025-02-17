from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.utils.crypto import get_random_string
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django import forms
import qrcode
import qrcode.image.svg
from io import BytesIO
from .models import ShortenedURL

# فرم ورود
class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

# صفحه لاگین
class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('dashboard')
        return render(request, 'login.html', {'form': form, 'error': 'Invalid credentials'})

# لاگ اوت کاربر
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

# فرم کوتاه کردن لینک
class URLShortenerForm(forms.Form):
    url = forms.URLField(label='Enter URL', required=True)

# ساخت لینک کوتاه
@login_required
class ShortenURLView(View):
    def get(self, request):
        form = URLShortenerForm()
        return render(request, 'shortener_form.html', {'form': form})

    def post(self, request):
        form = URLShortenerForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            shortened, created = ShortenedURL.objects.get_or_create(original_url=url, user=request.user)
            return render(request, 'shortener_form.html', {'form': form, 'short_url': request.build_absolute_uri(f'/{shortened.short_code}'), 'click_count': shortened.click_count})
        return render(request, 'shortener_form.html', {'form': form})

# ریدایرکت و افزایش تعداد کلیک
class RedirectURLView(View):
    def get(self, request, code):
        url_entry = get_object_or_404(ShortenedURL, short_code=code)
        url_entry.click_count += 1
        url_entry.save()
        return redirect(url_entry.original_url)

# آنالیتیکس لینک‌های هر کاربر
@login_required
class DashboardView(View):
    def get(self, request):
        user_links = ShortenedURL.objects.filter(user=request.user)
        return render(request, 'dashboard.html', {'links': user_links})

# تولید QR Code در فرمت SVG
class QRCodeSVGView(View):
    def get(self, request, code):
        url_entry = get_object_or_404(ShortenedURL, short_code=code)
        factory = qrcode.image.svg.SvgImage
        qr = qrcode.make(request.build_absolute_uri(f'/{code}'), image_factory=factory)
        stream = BytesIO()
        qr.save(stream)
        stream.seek(0)
        return HttpResponse(stream.getvalue(), content_type="image/svg+xml")
