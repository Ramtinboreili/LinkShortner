import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    """Bring the initial prototype schema up to the production model.

    `original_url` loses its global unique constraint (it prevented two users
    from ever shortening the same destination) and gains timestamps plus an
    index tuned for the dashboard query.
    """

    dependencies = [
        ("shortener", "0003_shortenedurl_user"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="shortenedurl",
            name="original_url",
            field=models.URLField(
                max_length=2048,
                validators=[django.core.validators.URLValidator(schemes=["http", "https"])],
            ),
        ),
        migrations.AlterField(
            model_name="shortenedurl",
            name="short_code",
            field=models.CharField(db_index=True, max_length=32, unique=True),
        ),
        migrations.AlterField(
            model_name="shortenedurl",
            name="click_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="shortenedurl",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="links",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="shortenedurl",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, db_index=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="shortenedurl",
            name="last_clicked_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterModelOptions(
            name="shortenedurl",
            options={"ordering": ("-created_at",)},
        ),
        migrations.AddIndex(
            model_name="shortenedurl",
            index=models.Index(
                fields=["user", "-created_at"], name="shortener_user_created_idx"
            ),
        ),
    ]
