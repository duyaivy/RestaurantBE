# Fix: DB column for category_id FK is "category_id" (not "category_id_id").
# Use SeparateDatabaseAndState to update Django's model state without touching the DB.

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0003_auto_20260226_1727'),
        ('dishes', '0005_auto_20260314_0036'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],  # No actual SQL — column already exists correctly
            state_operations=[
                migrations.AlterField(
                    model_name='dish',
                    name='category_id',
                    field=models.ForeignKey(
                        db_column='category_id',
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to='categories.category',
                    ),
                ),
            ],
        ),
    ]
