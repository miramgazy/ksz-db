import os
import csv
import re
from pathlib import Path
from datetime import datetime, timezone
from django.db import migrations

RU_MONTHS = {
    'янв': 1, 'фев': 2, 'мар': 3, 'апр': 4, 'май': 5, 'июн': 6,
    'июл': 7, 'авг': 8, 'сен': 9, 'окт': 10, 'ноя': 11, 'дек': 12
}

def parse_access_date(d_str):
    if not d_str:
        return None
    d_str = d_str.strip().lower()
    m = re.match(r'^(\d{1,2})\.([а-яё]+)\.(\d{2,4})$', d_str)
    if not m:
        return None
    day = int(m.group(1))
    mon_str = m.group(2)[:3]
    mon = RU_MONTHS.get(mon_str)
    year = int(m.group(3))
    if year < 100:
        year += 2000
    if not mon:
        return None
    return datetime(year, mon, day, tzinfo=timezone.utc)


def backfill_creation_dates(apps, schema_editor):
    Company = apps.get_model('companies', 'Company')
    candidates = [
        Path('/app/examles/main.csv'),
        Path(__file__).resolve().parents[4] / 'examles' / 'main.csv',
        Path(__file__).resolve().parents[3] / 'examles' / 'main.csv',
        Path.cwd() / 'examles' / 'main.csv',
    ]
    main_file = None
    for c in candidates:
        if c.exists():
            main_file = c
            break

    if not main_file:
        return

    with open(main_file, encoding='utf-8-sig', errors='ignore') as f:
        reader = csv.DictReader(f, delimiter=';')
        for r in reader:
            c_id = int(r['id']) if r.get('id') else None
            cd = r.get('CreationDate', '').strip()
            if c_id and cd:
                dt = parse_access_date(cd)
                if dt:
                    Company.objects.filter(id=c_id).update(created_at=dt)


def reverse_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0005_clean_iiko_versions'),
    ]

    operations = [
        migrations.RunPython(backfill_creation_dates, reverse_noop),
    ]
