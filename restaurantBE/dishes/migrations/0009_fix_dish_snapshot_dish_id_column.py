# Fix: DB column for dish_id FK is "dish_id" (not "dish_id_id").
# After migration 0003 created DishSnapshot with ForeignKey, Django created
# column "dish_id_id" (default behavior). This migration renames it back
# to "dish_id" in the actual database.
# Uses conditional SQL so it works on both fresh DB and existing DB (Supabase).

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dishes', '0008_auto_20260408_2211'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=[
                        # Rename dish_id_id -> dish_id only if the wrong column exists
                        """
                        DO $$
                        BEGIN
                            IF EXISTS (
                                SELECT 1 FROM information_schema.columns
                                WHERE table_name = 'dish_snapshot' AND column_name = 'dish_id_id'
                            ) AND NOT EXISTS (
                                SELECT 1 FROM information_schema.columns
                                WHERE table_name = 'dish_snapshot' AND column_name = 'dish_id'
                            ) THEN
                                ALTER TABLE dish_snapshot RENAME COLUMN dish_id_id TO dish_id;
                            END IF;
                        END $$;
                        """,
                        # If neither column exists (fresh DB), add dish_id column
                        """
                        DO $$
                        BEGIN
                            IF NOT EXISTS (
                                SELECT 1 FROM information_schema.columns
                                WHERE table_name = 'dish_snapshot' AND column_name = 'dish_id'
                            ) AND NOT EXISTS (
                                SELECT 1 FROM information_schema.columns
                                WHERE table_name = 'dish_snapshot' AND column_name = 'dish_id_id'
                            ) THEN
                                ALTER TABLE dish_snapshot ADD COLUMN dish_id BIGINT NULL;
                            END IF;
                        END $$;
                        """,
                    ],
                    reverse_sql=[
                        """
                        DO $$
                        BEGIN
                            IF EXISTS (
                                SELECT 1 FROM information_schema.columns
                                WHERE table_name = 'dish_snapshot' AND column_name = 'dish_id'
                            ) THEN
                                ALTER TABLE dish_snapshot DROP COLUMN dish_id;
                            END IF;
                        END $$;
                        """,
                    ],
                ),
            ],
            state_operations=[
                migrations.AlterField(
                    model_name='dishsnapshot',
                    name='dish_id',
                    field=models.ForeignKey(
                        db_column='dish_id',
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to='dishes.dish',
                    ),
                ),
            ],
        ),
    ]
