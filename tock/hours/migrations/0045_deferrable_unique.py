# Generated by Django 2.0.9 on 2019-01-17 18:28

from django.db import migrations


class Migration(migrations.Migration):
    """
    UNIQUE constraints are created by Django with the postgres default of NONDEFFERABLE
    Recreating TimeCardObject's UNIQUE constraint as DEFERRABLE
    """
    dependencies = [
        ('hours', '0044_delete_targets'),
    ]

    DROP_UNIQUE_CONSTRAINT = """
            ALTER TABLE public.hours_timecardobject
            DROP CONSTRAINT hours_timecardobject_timecard_id_project_id_b3d0a465_uniq
        """
    ADD_NON_DEFERRABLE = """
            ALTER TABLE public.hours_timecardobject
            ADD CONSTRAINT hours_timecardobject_timecard_id_project_id_b3d0a465_uniq
            UNIQUE (project_id, timecard_id)
        """
    ADD_DEFERRABLE = ADD_NON_DEFERRABLE + " DEFERRABLE"

    operations = [migrations.RunSQL(DROP_UNIQUE_CONSTRAINT, ADD_NON_DEFERRABLE),
                  migrations.RunSQL(ADD_DEFERRABLE, DROP_UNIQUE_CONSTRAINT)
                  ]
