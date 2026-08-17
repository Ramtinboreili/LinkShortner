# 🔗 LinkShortner

A production-ready URL shortener built with Django 5.2, PostgreSQL and Gunicorn.
Shorten links, pick custom aliases, share QR codes, and track clicks from a
dashboard — the whole stack runs from a single `docker compose up`.

---

## Features

- **Short links** with random collision-safe codes or your own custom alias
- **QR codes** for every link, previewable in-page and downloadable as SVG
- **Click tracking** with atomic counters that survive concurrent traffic
- **Dashboard** with search, pagination, per-link stats and deletion
- **Accounts** — registration, login, and strict per-user link isolation
- **Modern UI** — responsive, accessible, light/dark theme, zero external assets
- **Admin panel** for managing every user and link

---

## Quick start (Docker)

```sh
git clone https://github.com/Ramtinboreili/LinkShortner.git
cd LinkShortner

cp .env.example .env
# Set SECRET_KEY and POSTGRES_PASSWORD at minimum:
python3 -c "import secrets; print(secrets.token_urlsafe(50))"

docker compose up -d --build
```

The app is at <http://localhost:8000>. Migrations run automatically on boot.

Create an admin account:

```sh
docker compose exec web python manage.py createsuperuser
```

Or set `DJANGO_SUPERUSER_USERNAME` / `DJANGO_SUPERUSER_EMAIL` /
`DJANGO_SUPERUSER_PASSWORD` in `.env` and it is created on first start.

Useful commands:

```sh
docker compose logs -f web     # follow logs
docker compose exec web python manage.py test   # run the test suite
docker compose down            # stop (add -v to also drop the database volume)
```

---

## Local development (without Docker)

```sh
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env        # set DEBUG=True; SQLite is used when DATABASE_URL is unset
python manage.py migrate
python manage.py runserver
```

Run the tests with `python manage.py test`.

---

## Configuration

Everything is read from the environment — see [`.env.example`](.env.example).

| Variable | Default | Purpose |
| --- | --- | --- |
| `SECRET_KEY` | — | **Required** when `DEBUG=False` |
| `DEBUG` | `False` | Never enable in production |
| `ALLOWED_HOSTS` | empty | Comma-separated hostnames |
| `CSRF_TRUSTED_ORIGINS` | empty | Origins allowed to POST (needed behind HTTPS) |
| `DATABASE_URL` | SQLite file | e.g. `postgres://user:pass@db:5432/linkshortner` |
| `SITE_NAME` | `LinkShortner` | Branding shown in the UI |
| `SHORT_CODE_LENGTH` | `7` | Length of generated codes |
| `ALLOW_REGISTRATION` | `True` | Set `False` for a private instance |
| `SECURE_SSL_REDIRECT` | `False` | Enable once TLS terminates in front |
| `SECURE_HSTS_SECONDS` | `0` | e.g. `31536000` once HTTPS is stable |
| `LOG_LEVEL` | `INFO` | Root log level |

### Running behind a reverse proxy

The app trusts `X-Forwarded-Proto` for scheme detection. Terminate TLS at your
proxy, forward to `web:8000`, then set `SECURE_SSL_REDIRECT=True`,
`SECURE_HSTS_SECONDS=31536000`, and add your domain to both `ALLOWED_HOSTS`
and `CSRF_TRUSTED_ORIGINS`. Static files are served by WhiteNoise, so no
separate static-file container is needed.

---

## Project layout

```
config/                 Django project — settings, URLs, WSGI/ASGI entrypoints
shortener/
  models.py             ShortenedURL
  views.py              home, dashboard, redirect, QR, auth
  forms.py              shorten + auth forms
  urls.py               routes, incl. the root-level short-code catch-all
  utils.py              code generation, alias validation, reserved names
  templates/shortener/  base layout + pages
  static/shortener/     stylesheet and progressive-enhancement JS
  tests/                model and view tests
docker/entrypoint.sh    waits for the DB, migrates, then starts Gunicorn
Dockerfile              multi-stage build, non-root runtime
docker-compose.yml      web + postgres
```

---

## Security notes

- Only `http`/`https` destinations are accepted, so a short link can never
  redirect into a `javascript:` or `file:` URL.
- Reserved codes (`admin`, `login`, `dashboard`, …) cannot be claimed as aliases.
- Links are scoped to their owner: another user cannot list or delete them.
- Secure cookies, HSTS, `nosniff` and `X-Frame-Options: DENY` are enabled
  automatically whenever `DEBUG=False`.

---

## License

MIT
