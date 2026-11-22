import os
import csv
import re
from pathlib import Path
from datetime import datetime, timezone
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from apps.companies.models import Company, AnydeskStation, IikoDistribution, City, BusinessType, LicenceType, AnydeskVersion
from apps.companies.utils import clean_iiko_version
from apps.common.crypto import decrypt_password, encrypt_password

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

class Command(BaseCommand):
    help = 'Imports legacy MS Access database exports (main.csv, anydesk_list.csv, iikoOfficeLink.csv)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dir',
            type=str,
            default='',
            help='Directory containing the CSV files (defaults to examles/ in workspace or /app/examles in container)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing records before importing'
        )

    def find_csv_dir(self, custom_dir):
        if custom_dir and os.path.exists(custom_dir):
            return Path(custom_dir)

        # Check common paths
        candidates = [
            Path('/app/examles'),
            Path(__file__).resolve().parents[4] / 'examles',
            Path(__file__).resolve().parents[3] / 'examles',
            Path.cwd() / 'examles',
        ]
        for c in candidates:
            if c.exists() and (c / 'main.csv').exists():
                return c

        raise FileNotFoundError("Could not find examles directory containing main.csv")

    def reset_sequence(self, table_name, pk_col='id'):
        if connection.vendor == 'postgresql':
            with connection.cursor() as cursor:
                cursor.execute(
                    f"SELECT setval(pg_get_serial_sequence('{table_name}', '{pk_col}'), coalesce(max({pk_col}), 1)) FROM {table_name};"
                )

    def handle(self, *args, **options):
        csv_dir = self.find_csv_dir(options['dir'])
        self.stdout.write(f"Using CSV directory: {csv_dir}")

        if options['clear']:
            self.stdout.write(self.style.WARNING("Clearing existing data..."))
            AnydeskVersion.objects.all().delete()
            AnydeskStation.objects.all().delete()
            Company.objects.all().delete()
            City.objects.all().delete()
            BusinessType.objects.all().delete()
            LicenceType.objects.all().delete()
            IikoDistribution.objects.all().delete()

        # 1. Import main.csv -> Company
        main_file = csv_dir / 'main.csv'
        if main_file.exists():
            self.import_companies(main_file)
        else:
            self.stdout.write(self.style.ERROR(f"File not found: {main_file}"))

        # 2. Import anydesk_list.csv -> AnydeskStation
        anydesk_file = csv_dir / 'anydesk_list.csv'
        if anydesk_file.exists():
            self.import_anydesk(anydesk_file)
        else:
            self.stdout.write(self.style.ERROR(f"File not found: {anydesk_file}"))

        # 3. Import iikoOfficeLink.csv -> IikoDistribution
        distrib_file = csv_dir / 'iikoOfficeLink.csv'
        if distrib_file.exists():
            self.import_distributions(distrib_file)
        else:
            self.stdout.write(self.style.ERROR(f"File not found: {distrib_file}"))

        # 4. Import Anydesk_version.csv -> AnydeskVersion
        anydesk_ver_file = csv_dir / 'Anydesk_version.csv'
        if anydesk_ver_file.exists():
            self.import_anydesk_versions(anydesk_ver_file)
        else:
            self.stdout.write(self.style.WARNING(f"File not found: {anydesk_ver_file}"))

        self.stdout.write(self.style.SUCCESS("All imports completed successfully!"))

    def import_companies(self, filepath):
        self.stdout.write(f"Importing companies from {filepath}...")
        companies_to_create = []
        cities_set = set()

        raw_rows = []
        with open(filepath, 'r', encoding='utf-8-sig', errors='ignore') as f:
            reader = csv.DictReader(f, delimiter=';')
            raw_rows = list(reader)

        # First identify which IDs are referenced as Chains (sort_number points to them)
        referenced_sort_numbers = set()
        for r in raw_rows:
            sn = r.get('sort_number', '').strip()
            if sn.isdigit():
                referenced_sort_numbers.add(int(sn))

        for row in raw_rows:
            comp_id = int(row['id']) if row.get('id') else None
            if not comp_id:
                continue

            status_val = row.get('status', '').strip().upper()
            is_active = (status_val in ('ИСТИНА', 'TRUE', '1'))

            raw_pwd = row.get('system_admin_password', '').strip()
            plain_pwd = decrypt_password(raw_pwd)
            enc_pwd = encrypt_password(plain_pwd)

            sort_num = None
            if row.get('sort_number') and row['sort_number'].strip().isdigit():
                sort_num = int(row['sort_number'].strip())

            place_name = row.get('place_name', '').strip()
            iiko_ver = clean_iiko_version(row.get('iiko_version', '').strip())
            iiko_rosta = row.get('iiko_rosta', '').strip()
            city = row.get('city', '').strip()
            if city:
                cities_set.add(city)

            # Determine software_type: 2 -> ROSTA, else IIKO
            if iiko_rosta == '2':
                sw_type = Company.SoftwareType.ROSTA
            else:
                sw_type = Company.SoftwareType.IIKO

            # Determine node_type (CHAIN vs RMS)
            is_chain = (
                comp_id in referenced_sort_numbers or
                sort_num == comp_id or
                'Chain' in iiko_ver or
                '-CO' in place_name or
                ' CO' in place_name
            )
            node_type = Company.NodeType.CHAIN if is_chain else Company.NodeType.RMS

            created_at_val = parse_access_date(row.get('CreationDate', '').strip())

            comp_kwargs = dict(
                id=comp_id,
                software_type=sw_type,
                node_type=node_type,
                parent_chain_id=None,  # Will link in second pass
                place_name=place_name,
                company_name=row.get('company_name', '').strip(),
                cabinet_name=row.get('cabinet_name', '').strip(),
                crm_id=row.get('crm_id', '').strip(),
                uid=row.get('uid', '').strip(),
                system_admin_name=row.get('system_admin_name', '').strip() or 'iikoadm',
                system_admin_password_enc=enc_pwd,
                business_type=row.get('business_type', '').strip(),
                licence_type=row.get('licence_type', '').strip(),
                iiko_version=iiko_ver,
                server_name=row.get('server_name', '').strip(),
                port_number=row.get('port_number', '').strip() or '443',
                image_link=row.get('image_link', '').strip(),
                no_ip=row.get('noIP', '').strip(),
                iiko_rosta=iiko_rosta,
                sort_number=sort_num,
                helpdesk_its=row.get('helpDesk_its', '').strip(),
                city=city,
                status=is_active,
                iiko_web_address=row.get('iikoWebAddres', '').strip(),
            )
            if created_at_val:
                comp_kwargs['created_at'] = created_at_val

            comp = Company(**comp_kwargs)
            companies_to_create.append(comp)

        with transaction.atomic():
            # 1. Populate Cities, Business Types, Licence Types
            for c_name in sorted(cities_set):
                City.objects.get_or_create(name=c_name)

            for bt in set(c.business_type for c in companies_to_create if c.business_type):
                BusinessType.objects.get_or_create(name=bt)

            for lt in set(c.licence_type for c in companies_to_create if c.licence_type):
                LicenceType.objects.get_or_create(name=lt)

            # 2. Bulk create Companies
            Company.objects.bulk_create(companies_to_create, ignore_conflicts=True)
            self.reset_sequence('companies_company')

            # 3. Second pass: link branches to their parent_chain
            all_chain_ids = set(Company.objects.filter(node_type=Company.NodeType.CHAIN).values_list('id', flat=True))
            branches_to_update = []
            for comp in Company.objects.filter(sort_number__isnull=False):
                if comp.sort_number != comp.id and comp.sort_number in all_chain_ids:
                    comp.parent_chain_id = comp.sort_number
                    branches_to_update.append(comp)

            if branches_to_update:
                Company.objects.bulk_update(branches_to_update, ['parent_chain'])

        self.stdout.write(self.style.SUCCESS(
            f"Imported {len(companies_to_create)} companies ({len(cities_set)} cities, {len(branches_to_update)} branches linked to Chains)."
        ))

    def import_anydesk(self, filepath):
        self.stdout.write(f"Importing AnyDesk stations from {filepath}...")
        stations_to_create = []
        valid_company_ids = set(Company.objects.values_list('id', flat=True))

        with open(filepath, 'r', encoding='utf-8-sig', errors='ignore') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                st_id = int(row['id']) if row.get('id') else None
                company_id = int(row['company_id']) if row.get('company_id') else None

                if not st_id or not company_id or company_id not in valid_company_ids:
                    continue

                st = AnydeskStation(
                    id=st_id,
                    company_id=company_id,
                    description=row.get('description', '').strip(),
                    anydesk_id=row.get('anydesk_id', '').strip(),
                    any_pass=row.get('any_pass', '').strip(),
                )
                stations_to_create.append(st)

        with transaction.atomic():
            AnydeskStation.objects.bulk_create(stations_to_create, ignore_conflicts=True)
            self.reset_sequence('companies_anydeskstation')

        self.stdout.write(self.style.SUCCESS(f"Imported {len(stations_to_create)} AnyDesk stations."))

    def import_distributions(self, filepath):
        self.stdout.write(f"Importing iiko distributions from {filepath}...")
        dist_to_create = []

        with open(filepath, 'r', encoding='utf-8-sig', errors='ignore') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                d_id = int(row['id']) if row.get('id') else None
                dist = IikoDistribution(
                    id=d_id,
                    iiko_version=clean_iiko_version(row.get('iiko_version', '').strip()),
                    type=row.get('type', '').strip() or 'RMS',
                    link_ya=row.get('linkYa', '').strip(),
                )
                dist_to_create.append(dist)

        with transaction.atomic():
            IikoDistribution.objects.bulk_create(dist_to_create, ignore_conflicts=True)
            self.reset_sequence('companies_iikodistribution')

        self.stdout.write(self.style.SUCCESS(f"Imported {len(dist_to_create)} iiko distributions."))

    def import_anydesk_versions(self, filepath):
        self.stdout.write(f"Importing AnyDesk versions from {filepath}...")
        versions_to_create = []

        with open(filepath, 'r', encoding='utf-8-sig', errors='ignore') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                v_id = int(row['id']) if row.get('id') else None
                is_sb = row.get('IsSandbox', '').strip().upper() in ('ИСТИНА', 'TRUE', '1')
                is_def = (v_id == 1)

                ver = AnydeskVersion(
                    id=v_id,
                    name=row.get('VersionName', '').strip(),
                    exe_path=row.get('ExePath', '').strip(),
                    is_sandbox=is_sb,
                    sandbox_params=row.get('SandboxParams', '').strip(),
                    is_default=is_def,
                    order=v_id or 0,
                )
                versions_to_create.append(ver)

        with transaction.atomic():
            AnydeskVersion.objects.bulk_create(versions_to_create, ignore_conflicts=True)
            self.reset_sequence('companies_anydeskversion')

        self.stdout.write(self.style.SUCCESS(f"Imported {len(versions_to_create)} AnyDesk profiles/versions."))
