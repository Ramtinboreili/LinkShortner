from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from shortener.models import ShortenedURL


class HomeViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alice", password="pw-for-tests-123")

    def test_landing_page_is_public(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_anonymous_post_is_redirected_to_login(self):
        response = self.client.post(reverse("home"), {"original_url": "https://example.com"})
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response["Location"])
        self.assertEqual(ShortenedURL.objects.count(), 0)

    def test_authenticated_user_can_shorten(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("home"), {"original_url": "https://example.com/page"})
        self.assertEqual(response.status_code, 200)
        link = ShortenedURL.objects.get()
        self.assertEqual(link.user, self.user)
        self.assertContains(response, link.short_code)

    def test_repeated_url_reuses_the_existing_link(self):
        self.client.force_login(self.user)
        for _ in range(2):
            self.client.post(reverse("home"), {"original_url": "https://example.com/page"})
        self.assertEqual(ShortenedURL.objects.count(), 1)

    def test_custom_alias_is_used(self):
        self.client.force_login(self.user)
        self.client.post(
            reverse("home"),
            {"original_url": "https://example.com/page", "short_code": "my-alias"},
        )
        self.assertTrue(ShortenedURL.objects.filter(short_code="my-alias").exists())

    def test_taken_alias_is_rejected(self):
        ShortenedURL.objects.create(user=self.user, original_url="https://a.test", short_code="taken")
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("home"), {"original_url": "https://b.test", "short_code": "taken"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(ShortenedURL.objects.count(), 1)

    def test_reserved_alias_is_rejected(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("home"), {"original_url": "https://b.test", "short_code": "admin"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(ShortenedURL.objects.count(), 0)


class RedirectTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alice", password="pw-for-tests-123")
        self.link = ShortenedURL.objects.create(
            user=self.user, original_url="https://example.com/page", short_code="abc123"
        )

    def test_redirects_and_counts_the_click(self):
        response = self.client.get(f"/{self.link.short_code}")
        self.assertRedirects(response, "https://example.com/page", fetch_redirect_response=False)
        self.link.refresh_from_db()
        self.assertEqual(self.link.click_count, 1)
        self.assertIsNotNone(self.link.last_clicked_at)

    def test_unknown_code_returns_404(self):
        self.assertEqual(self.client.get("/nope999").status_code, 404)

    def test_reserved_path_without_slash_redirects_to_the_real_page(self):
        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], "/dashboard/")

    def test_named_routes_are_not_shadowed_by_the_catch_all(self):
        self.assertEqual(self.client.get(reverse("login")).status_code, 200)


class DashboardTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alice", password="pw-for-tests-123")
        self.other = User.objects.create_user("bob", password="pw-for-tests-123")
        self.mine = ShortenedURL.objects.create(
            user=self.user, original_url="https://mine.test", short_code="mine01"
        )
        self.theirs = ShortenedURL.objects.create(
            user=self.other, original_url="https://theirs.test", short_code="thei01"
        )

    def test_requires_login(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_only_shows_own_links(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, "mine01")
        self.assertNotContains(response, "thei01")

    def test_search_filters_results(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("dashboard"), {"q": "nothing-matches"})
        self.assertNotContains(response, "mine01")

    def test_user_cannot_delete_another_users_link(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("delete_link", kwargs={"pk": self.theirs.pk}))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(ShortenedURL.objects.filter(pk=self.theirs.pk).exists())

    def test_user_can_delete_own_link(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("delete_link", kwargs={"pk": self.mine.pk}))
        self.assertRedirects(response, reverse("dashboard"))
        self.assertFalse(ShortenedURL.objects.filter(pk=self.mine.pk).exists())


class QRCodeTests(TestCase):
    def test_returns_svg(self):
        user = User.objects.create_user("alice", password="pw-for-tests-123")
        ShortenedURL.objects.create(
            user=user, original_url="https://example.com", short_code="qr1234"
        )
        response = self.client.get(reverse("qrcode_svg", kwargs={"code": "qr1234"}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/svg+xml")
        self.assertIn(b"<svg", response.content)

    def test_download_sets_attachment_header(self):
        user = User.objects.create_user("alice", password="pw-for-tests-123")
        ShortenedURL.objects.create(
            user=user, original_url="https://example.com", short_code="qr1234"
        )
        response = self.client.get(
            reverse("qrcode_svg", kwargs={"code": "qr1234"}), {"download": "1"}
        )
        self.assertIn("attachment", response["Content-Disposition"])


class AuthTests(TestCase):
    def test_registration_creates_and_logs_in_a_user(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newcomer",
                "password1": "a-strong-passphrase-42",
                "password2": "a-strong-passphrase-42",
            },
        )
        self.assertRedirects(response, reverse("dashboard"))
        self.assertTrue(User.objects.filter(username="newcomer").exists())

    def test_healthz(self):
        response = self.client.get(reverse("healthz"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
