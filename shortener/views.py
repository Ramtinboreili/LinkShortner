from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views import View
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.utils.crypto import get_random_string
from django import forms
from io import BytesIO
from .models import ShortenedURL
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import ShortenedURL
import qrcode
import qrcode.image.svg
from io import BytesIO
from django.http import HttpResponse
from django.views import View
from .models import ShortenedURL
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ShortenedURL

class ShortenURLView(View):
    def post(self, request):
        url = request.POST.get("url")
        if not url:
            messages.error(request, "Please enter a valid URL.")
            return redirect("shorten_url")

        # چک کن که آیا URL قبلاً برای همان کاربر ساخته شده است یا نه
        shortened, created = ShortenedURL.objects.get_or_create(original_url=url, defaults={"user": request.user})

        if not created:
            messages.info(request, "This URL is already shortened.")
        
        return render(request, "shortener_form.html", {"short_url": request.build_absolute_uri(shortened.short_code)})

class QRCodeSVGView(View):
    def get(self, request, code):
        try:
            link = ShortenedURL.objects.get(short_code=code)
            qr = qrcode.make(link.original_url, image_factory=qrcode.image.svg.SvgImage)
            stream = BytesIO()
            qr.save(stream)
            response = HttpResponse(stream.getvalue(), content_type="image/svg+xml")
            response["Content-Disposition"] = f'attachment; filename="{code}.svg"'
            return response
        except ShortenedURL.DoesNotExist:
            return HttpResponse("Invalid Link", status=404)


def QRCodeSVGView(request, code):
    try:
        link = ShortenedURL.objects.get(short_code=code)
        qr = qrcode.make(link.original_url, image_factory=qrcode.image.svg.SvgImage)
        stream = BytesIO()
        qr.save(stream)
        response = HttpResponse(stream.getvalue(), content_type="image/svg+xml")
        response["Content-Disposition"] = f'attachment; filename="{code}.svg"'
        return response
    except ShortenedURL.DoesNotExist:
        return HttpResponse("Invalid Link", status=404)

# **🔹 فرم ورود کاربران**
class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


# **🔹 صفحه ورود کاربران**
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


# **🔹 خروج از حساب کاربری**
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


# **🔹 فرم کوتاه کردن لینک**
class URLShortenerForm(forms.Form):
    url = forms.URLField(label='Enter URL', required=True)


# **🔹 کوتاه کردن لینک و نمایش آن**
@method_decorator(login_required, name='dispatch')
class ShortenURLView(View):
    def get(self, request):
        form = URLShortenerForm()
        return render(request, 'shortener_form.html', {'form': form})

    def post(self, request):
        form = URLShortenerForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            shortened, created = ShortenedURL.objects.get_or_create(original_url=url, user=request.user)
            return render(request, 'shortener_form.html', {
                'form': form,
                'short_url': request.build_absolute_uri(f'/{shortened.short_code}'),
                'click_count': shortened.click_count
            })
        return render(request, 'shortener_form.html', {'form': form})


# **🔹 هدایت به لینک اصلی و شمارش کلیک‌ها**
class RedirectURLView(View):
    def get(self, request, code):
        url_entry = get_object_or_404(ShortenedURL, short_code=code)
        url_entry.click_count += 1
        url_entry.save()
        return redirect(url_entry.original_url)


# **🔹 داشبورد کاربران - نمایش لینک‌های ساخته شده**
@method_decorator(login_required, name='dispatch')
class DashboardView(View):
    def get(self, request):
        user_links = ShortenedURL.objects.filter(user=request.user)
        return render(request, 'dashboard.html', {'links': user_links})


# **🔹 تولید QR Code در فرمت SVG**
class QRCodeSVGView(View):
    def get(self, request, code):
        url_entry = get_object_or_404(ShortenedURL, short_code=code)
        factory = qrcode.image.svg.SvgImage
        qr = qrcode.make(request.build_absolute_uri(f'/{code}'), image_factory=factory)
        stream = BytesIO()
        qr.save(stream)
        stream.seek(0)
        return HttpResponse(stream.getvalue(), content_type="image/svg+xml")

# صفحه لاگین
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            return render(request, "login.html", {"error": "Invalid credentials"})
    return render(request, "login.html")

# صفحه داشبورد
@login_required
def dashboard(request):
    links = ShortenedURL.objects.filter(user=request.user)
    return render(request, "dashboard.html", {"links": links})

# خروج از حساب
def logout_view(request):
    logout(request)
    return redirect("login")
