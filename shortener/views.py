import logging
from io import BytesIO

import qrcode
import qrcode.image.svg
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.db import DatabaseError, models
from django.db.models import F, Sum
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, ListView

from .forms import RegisterForm, ShortenURLForm
from .models import ShortenedURL
from .utils import RESERVED_CODES

logger = logging.getLogger(__name__)


class HomeView(View):
    """Landing page with the shorten form.

    Anonymous visitors can see the page but are sent to the login screen when
    they submit, so the link always has an owner.
    """

    template_name = "shortener/home.html"

    def get(self, request):
        return render(request, self.template_name, {"form": ShortenURLForm()})

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), settings.LOGIN_URL)

        form = ShortenURLForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form}, status=400)

        url = form.cleaned_data["original_url"]
        custom_code = form.cleaned_data["short_code"]

        link = None
        if not custom_code:
            # Re-use the existing link instead of handing out a second code for
            # the same destination. A custom alias is an explicit request for a
            # new one, so it always creates a fresh link.
            link = ShortenedURL.objects.filter(
                user=request.user, original_url=url
            ).first()
            if link:
                messages.info(request, "You already had a short link for this URL.")

        if link is None:
            link = ShortenedURL.objects.create(
                user=request.user, original_url=url, short_code=custom_code
            )
            messages.success(request, "Short link created.")

        return render(
            request,
            self.template_name,
            {"form": ShortenURLForm(), "link": link, "short_url": link.build_short_url(request)},
        )


class DashboardView(LoginRequiredMixin, ListView):
    """Paginated list of the current user's links."""

    template_name = "shortener/dashboard.html"
    context_object_name = "links"
    paginate_by = 20

    def get_queryset(self):
        queryset = ShortenedURL.objects.filter(user=self.request.user)
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                models.Q(original_url__icontains=query)
                | models.Q(short_code__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        totals = ShortenedURL.objects.filter(user=self.request.user).aggregate(
            total_links=models.Count("id"), total_clicks=Sum("click_count")
        )
        context["query"] = self.request.GET.get("q", "")
        context["total_links"] = totals["total_links"] or 0
        context["total_clicks"] = totals["total_clicks"] or 0
        return context


class DeleteLinkView(LoginRequiredMixin, View):
    """Delete one of the current user's links."""

    def post(self, request, pk):
        link = get_object_or_404(ShortenedURL, pk=pk, user=request.user)
        link.delete()
        messages.success(request, f"Deleted /{link.short_code}.")
        return redirect("dashboard")


class RedirectURLView(View):
    """Resolve a short code and send the visitor to the destination."""

    def get(self, request, code):
        try:
            link = ShortenedURL.objects.get(short_code=code)
        except ShortenedURL.DoesNotExist:
            # `/dashboard` and friends land here because the catch-all matches
            # before APPEND_SLASH gets a chance; send them to the real page.
            if code.lower() in RESERVED_CODES:
                return redirect(f"/{code}/", permanent=True)
            raise Http404("Unknown short link.")

        # Update in the database rather than on the instance so that concurrent
        # hits on the same link cannot overwrite each other's counts.
        try:
            ShortenedURL.objects.filter(pk=link.pk).update(
                click_count=F("click_count") + 1, last_clicked_at=timezone.now()
            )
        except DatabaseError:  # a failed count must never break the redirect
            logger.exception("Failed to record click for %s", code)
        return redirect(link.original_url)


class QRCodeView(View):
    """Return the short link's QR code as SVG (inline, or as a download)."""

    def get(self, request, code):
        link = get_object_or_404(ShortenedURL, short_code=code)
        image = qrcode.make(
            link.build_short_url(request),
            image_factory=qrcode.image.svg.SvgPathImage,
            box_size=12,
            border=2,
        )
        stream = BytesIO()
        image.save(stream)

        response = HttpResponse(stream.getvalue(), content_type="image/svg+xml")
        if "download" in request.GET:
            response["Content-Disposition"] = f'attachment; filename="{code}.svg"'
        response["Cache-Control"] = "public, max-age=86400"
        return response


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "shortener/register.html"
    success_url = reverse_lazy("dashboard")

    def dispatch(self, request, *args, **kwargs):
        if not settings.ALLOW_REGISTRATION:
            raise Http404
        if request.user.is_authenticated:
            return redirect("dashboard")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, f"Welcome, {self.object.username}!")
        return response


def healthz(request):
    """Liveness/readiness probe used by the container healthcheck."""
    return JsonResponse({"status": "ok"})
