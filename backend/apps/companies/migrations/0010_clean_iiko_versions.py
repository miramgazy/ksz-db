import re
from django.db import migrations


def clean_iiko_version(v: str) -> str:
    if not v:
        return ''
    v = str(v).strip()
    m = re.match(r'^(\d{1,2})[./](\d{1,2})[./](\d{4})(.*)$', v)
    if m:
        major = int(m.group(1))
        minor = int(m.group(2))
        year = int(m.group(3))
        patch = year - 2000 if year >= 2000 else year
        extra = m.group(4) or ''
        v = f"{major}.{minor}.{patch}{extra}"
    v = re.sub(r'[\s\-_/]+(RMS|Chain|Chains|РМС|Чейн)$', '', v, flags=re.IGNORECASE).strip()
    v = v.strip(' -_/')
    return v


def clean_existing_versions(apps, schema_editor):
    IikoDistribution = apps.get_model('companies', 'IikoDistribution')
    Company = apps.get_model('companies', 'Company')

    # 1. Clean IikoDistribution
    for dist in IikoDistribution.objects.all():
        cleaned = clean_iiko_version(dist.iiko_version)
        if cleaned != dist.iiko_version:
            dist.iiko_version = cleaned
            dist.save(update_fields=['iiko_version'])

    # 2. Clean Company
    for comp in Company.objects.filter(iiko_version__isnull=False).exclude(iiko_version=''):
        cleaned = clean_iiko_version(comp.iiko_version)
        if cleaned != comp.iiko_version:
            comp.iiko_version = cleaned
            comp.save(update_fields=['iiko_version'])


def reverse_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0009_companyservice_quantity_and_more'),
    ]

    operations = [
        migrations.RunPython(clean_existing_versions, reverse_noop),
    ]
