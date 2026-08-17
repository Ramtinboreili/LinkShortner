from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from shortener.models import ShortenedURL
from shortener.utils import CODE_ALPHABET, validate_short_code


class ShortenedURLModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alice", password="pw-for-tests-123")

    def test_short_code_is_generated_when_missing(self):
        link = ShortenedURL.objects.create(user=self.user, original_url="https://example.com")
        self.assertTrue(link.short_code)
        self.assertTrue(set(link.short_code) <= set(CODE_ALPHABET))

    def test_explicit_short_code_is_kept(self):
        link = ShortenedURL.objects.create(
            user=self.user, original_url="https://example.com", short_code="my-link"
        )
        self.assertEqual(link.short_code, "my-link")

    def test_same_url_can_be_shortened_by_different_users(self):
        bob = User.objects.create_user("bob", password="pw-for-tests-123")
        ShortenedURL.objects.create(user=self.user, original_url="https://example.com")
        ShortenedURL.objects.create(user=bob, original_url="https://example.com")
        self.assertEqual(ShortenedURL.objects.count(), 2)

    def test_non_http_scheme_is_rejected(self):
        link = ShortenedURL(user=self.user, original_url="javascript:alert(1)")
        with self.assertRaises(ValidationError):
            link.full_clean()


class ValidateShortCodeTests(TestCase):
    def test_reserved_code_is_rejected(self):
        with self.assertRaises(ValidationError):
            validate_short_code("admin")

    def test_illegal_characters_are_rejected(self):
        with self.assertRaises(ValidationError):
            validate_short_code("has spaces")

    def test_valid_code_passes(self):
        validate_short_code("my_link-2")
