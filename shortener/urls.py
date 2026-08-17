from django.contrib.auth import views as auth_views
from django.urls import path, register_converter

from . import views
from .forms import LoginForm
from .utils import MAX_CODE_LENGTH, MIN_CODE_LENGTH


class ShortCodeConverter:
    """Match only strings that could be a short code.

    Keeping the pattern tight stops the catch-all redirect route from
    swallowing unrelated paths (and turning 404s into misleading ones).
    """

    regex = rf"[A-Za-z0-9_-]{{{MIN_CODE_LENGTH},{MAX_CODE_LENGTH}}}"

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


register_converter(ShortCodeConverter, "code")

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("healthz", views.healthz, name="healthz"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("links/<int:pk>/delete/", views.DeleteLinkView.as_view(), name="delete_link"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="shortener/login.html",
            authentication_form=LoginForm,
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("qr/<code:code>.svg", views.QRCodeView.as_view(), name="qrcode_svg"),
    # Catch-all: must stay last so it cannot shadow the routes above.
    path("<code:code>", views.RedirectURLView.as_view(), name="redirect_url"),
]
