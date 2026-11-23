from django.db import migrations


def cleanup_inactive_companies_its(apps, schema_editor):
    Company = apps.get_model('companies', 'Company')
    # Services are provided only to active establishments.
    # Inactive establishments (status=False) must not have active ITS.
    Company.objects.filter(status=False, helpdesk_its='Да').update(
        helpdesk_its='Нет',
        its_expires_at=None,
        its_cost=0
    )


def reverse_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0010_clean_iiko_versions'),
    ]

    operations = [
        migrations.RunPython(cleanup_inactive_companies_its, reverse_noop),
    ]
