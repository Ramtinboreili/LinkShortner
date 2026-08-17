from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.validators import URLValidator

from .models import ShortenedURL
from .utils import MAX_CODE_LENGTH, validate_short_code


class ShortenURLForm(forms.ModelForm):
    """Shorten a URL, optionally under a user-chosen alias."""

    original_url = forms.URLField(
        label="Destination URL",
        max_length=2048,
        assume_scheme="https",
        validators=[URLValidator(schemes=["http", "https"])],
        widget=forms.URLInput(
            attrs={
                "placeholder": "https://example.com/a-very-long-link",
                "autocomplete": "off",
                "autofocus": True,
            }
        ),
    )
    short_code = forms.CharField(
        label="Custom alias (optional)",
        required=False,
        max_length=MAX_CODE_LENGTH,
        validators=[validate_short_code],
        widget=forms.TextInput(attrs={"placeholder": "my-link", "autocomplete": "off"}),
    )

    class Meta:
        model = ShortenedURL
        fields = ("original_url", "short_code")

    def clean_short_code(self):
        code = self.cleaned_data.get("short_code", "").strip()
        if code and ShortenedURL.objects.filter(short_code__iexact=code).exists():
            raise forms.ValidationError("That alias is already taken.")
        return code


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"placeholder": "Username", "autofocus": True}
        )
        self.fields["password"].widget.attrs.update({"placeholder": "Password"})


class RegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"placeholder": "Username", "autofocus": True}
        )
        self.fields["password1"].widget.attrs.update({"placeholder": "Password"})
        self.fields["password2"].widget.attrs.update({"placeholder": "Repeat password"})
