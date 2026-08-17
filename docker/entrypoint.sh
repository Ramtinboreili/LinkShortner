#!/usr/bin/env bash
# Wait for the database, apply migrations, then hand over to the CMD.
set -euo pipefail

echo "==> Waiting for the database…"
python - <<'PY'
import os
import sys
import time

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db import connections
from django.db.utils import OperationalError

deadline = time.monotonic() + float(os.environ.get("DB_WAIT_TIMEOUT", "60"))
while True:
    try:
        connections["default"].ensure_connection()
        break
    except OperationalError as exc:
        if time.monotonic() >= deadline:
            sys.exit(f"Database unreachable: {exc}")
        time.sleep(1)
PY

echo "==> Applying migrations…"
python manage.py migrate --noinput

# Optional convenience for first boot; skipped entirely when unset.
if [[ -n "${DJANGO_SUPERUSER_USERNAME:-}" && -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]]; then
  echo "==> Ensuring superuser '${DJANGO_SUPERUSER_USERNAME}' exists…"
  python manage.py createsuperuser --noinput --skip-checks || true
fi

echo "==> Starting: $*"
exec "$@"
