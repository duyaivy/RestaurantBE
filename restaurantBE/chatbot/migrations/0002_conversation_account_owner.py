from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("chatbot", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="conversation",
            name="account",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="chat_conversations",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RemoveConstraint(
            model_name="conversation",
            name="conversation_has_guest_or_session",
        ),
        migrations.AddConstraint(
            model_name="conversation",
            constraint=models.CheckConstraint(
                check=models.Q(
                    ("account__isnull", False),
                    ("guest__isnull", False),
                    ("session_key__isnull", False),
                    _connector="OR",
                ),
                name="conversation_has_owner",
            ),
        ),
        migrations.AddIndex(
            model_name="conversation",
            index=models.Index(
                fields=["account", "created_at"], name="chatbot_con_account_91f31d_idx"
            ),
        ),
    ]
