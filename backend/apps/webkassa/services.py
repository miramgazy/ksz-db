import csv
import io
import re
from datetime import datetime
from django.db import transaction
from apps.companies.models import Company
from .models import WebkassaCTO, WebkassaCashRegister


def clean_bin_iin(raw_val: str) -> str:
    """Очищает и нормализует строку БИН/ИИН."""
    if not raw_val:
        return ''
    cleaned = re.sub(r'\D', '', str(raw_val).strip())
    # Если Excel обрезал ведущий 0 в 12-значном БИН/ИИН
    if 9 <= len(cleaned) < 12:
        return cleaned.zfill(12)
    return cleaned


def parse_webkassa_date(raw_date: str):
    """Парсит дату окончания срока действия кассы."""
    if not raw_date:
        return None
    cleaned = str(raw_date).strip()
    if not cleaned:
        return None
    for fmt in ('%d.%m.%Y', '%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'):
        try:
            return datetime.strptime(cleaned, fmt).date()
        except ValueError:
            continue
    return None


def find_matching_company(bin_iin: str, organization: str):
    """
    Алгоритм поиска заведения / сети для автопривязки кассы:
    Привязка делается к юридическому лицу или головной сети (Chain).
    Если нет ни того, ни другого, или есть неоднозначность — возвращается None.
    """
    clean_bin = clean_bin_iin(bin_iin)
    
    # 1. Поиск по БИН / ИИН
    if clean_bin:
        # Ищем компании с таким БИН (проверяем нормализованный БИН и исходный)
        matching_companies = Company.objects.filter(bin=clean_bin)
        if not matching_companies.exists() and bin_iin.strip():
            matching_companies = Company.objects.filter(bin=bin_iin.strip())

        if matching_companies.exists():
            # Приоритет 1: Головная организация сети (Chain)
            chain_comp = matching_companies.filter(node_type=Company.NodeType.CHAIN).first()
            if chain_comp:
                return chain_comp
            
            # Приоритет 2: Если заведение ровно одно с таким БИН — привязываем к нему
            if matching_companies.count() == 1:
                return matching_companies.first()
            
            # Если найдено несколько точек, проверяем, есть ли у них общий parent_chain
            parent_ids = set(matching_companies.exclude(parent_chain__isnull=True).values_list('parent_chain_id', flat=True))
            if len(parent_ids) == 1:
                common_chain = Company.objects.filter(id=list(parent_ids)[0]).first()
                if common_chain:
                    return common_chain
            
            # Если есть несколько разрозненных точек без чейна — оставляем None для ручного выбора
            return None

    # 2. Фолбэк: поиск по совпадению company_name (Юр. лицо) или place_name с названием организации
    org_clean = (organization or '').strip().strip('"').strip('«»').strip("'").strip()
    if org_clean and len(org_clean) >= 3:
        # Проверяем точное совпадение с Юр. лицом (company_name)
        comp_by_org = Company.objects.filter(company_name__iexact=org_clean)
        if comp_by_org.exists():
            chain_match = comp_by_org.filter(node_type=Company.NodeType.CHAIN).first()
            if chain_match:
                return chain_match
            if comp_by_org.count() == 1:
                return comp_by_org.first()

    return None


def import_webkassa_csv(file_bytes: bytes, cto_name: str) -> dict:
    """
    Импортирует CSV файл WebKassa с разделителем ';' и привязкой к указанному ЦТО.
    Возвращает статистику импорта.
    """
    cto_clean = (cto_name or '').strip()
    if cto_clean:
        # Сохраняем ЦТО в справочник истории
        WebkassaCTO.objects.get_or_create(name=cto_clean)

    # Декодируем файл (поддержка UTF-8-SIG, UTF-8, Windows-1251)
    text = None
    for enc in ('utf-8-sig', 'utf-8', 'cp1251', 'latin1'):
        try:
            text = file_bytes.decode(enc)
            break
        except UnicodeDecodeError:
            continue

    if text is None:
        raise ValueError('Не удалось распознать кодировку CSV файла. Используйте UTF-8 или Windows-1251.')

    # Читаем CSV с разделителем ';'
    stream = io.StringIO(text)
    reader = csv.reader(stream, delimiter=';')

    total_rows = 0
    created_count = 0
    updated_count = 0
    matched_count = 0
    unmatched_count = 0

    header_mapped = False
    col_idx = {
        'name': 1,
        'serial': 2,
        'status': 3,
        'ofd': 4,
        'bin': 5,
        'org': 6,
        'expires': 7,
    }

    with transaction.atomic():
        for row in reader:
            if not row or not any(field.strip() for field in row):
                continue

            # Проверяем заголовок таблицы
            row_str = " ".join(row).lower()
            if 'заводской номер' in row_str or 'название кассы' in row_str:
                header_mapped = True
                # Определяем индексы колонок динамически по заголовку
                for idx, cell in enumerate(row):
                    cell_clean = cell.strip().lower()
                    if 'название кассы' in cell_clean:
                        col_idx['name'] = idx
                    elif 'заводской номер' in cell_clean:
                        col_idx['serial'] = idx
                    elif 'статус' in cell_clean:
                        col_idx['status'] = idx
                    elif 'офд' in cell_clean:
                        col_idx['ofd'] = idx
                    elif 'бин' in cell_clean:
                        col_idx['bin'] = idx
                    elif 'организация' in cell_clean:
                        col_idx['org'] = idx
                    elif 'сроки' in cell_clean or 'срок' in cell_clean:
                        col_idx['expires'] = idx
                continue

            # Данные строки
            serial = row[col_idx['serial']].strip() if len(row) > col_idx['serial'] else ''
            if not serial:
                continue

            total_rows += 1

            name = row[col_idx['name']].strip() if len(row) > col_idx['name'] else ''
            status = row[col_idx['status']].strip() if len(row) > col_idx['status'] else ''
            ofd = row[col_idx['ofd']].strip() if len(row) > col_idx['ofd'] else ''
            bin_raw = row[col_idx['bin']].strip() if len(row) > col_idx['bin'] else ''
            org = row[col_idx['org']].strip() if len(row) > col_idx['org'] else ''
            expires_raw = row[col_idx['expires']].strip() if len(row) > col_idx['expires'] else ''

            expires_date = parse_webkassa_date(expires_raw)
            bin_clean = clean_bin_iin(bin_raw)

            # Ищем существующую кассу по Заводскому номеру (serial_number)
            reg = WebkassaCashRegister.objects.filter(serial_number=serial).first()

            if reg:
                # Обновление существующей кассы
                reg.name = name or reg.name
                reg.status = status or reg.status
                reg.ofd = ofd or reg.ofd
                reg.bin_iin = bin_clean or reg.bin_iin
                reg.organization = org or reg.organization
                if expires_date:
                    reg.expires_at = expires_date
                if cto_clean:
                    reg.cto = cto_clean
                if status and status.strip().lower() == 'заблокирована':
                    reg.is_active = False

                # Если касса еще НЕ была привязана к заведению, пробуем привязать
                if not reg.company_id:
                    matched_comp = find_matching_company(bin_clean or bin_raw, org)
                    if matched_comp:
                        reg.company = matched_comp
                        reg.auto_matched = True
                        matched_count += 1
                        # Если у компании не был указан БИН, заполняем его
                        if bin_clean and not matched_comp.bin:
                            matched_comp.bin = bin_clean
                            matched_comp.save(update_fields=['bin'])
                    else:
                        unmatched_count += 1
                else:
                    if reg.auto_matched:
                        matched_count += 1

                reg.save()
                updated_count += 1
            else:
                # Создание новой кассы
                matched_comp = find_matching_company(bin_clean or bin_raw, org)
                auto_matched = False
                if matched_comp:
                    auto_matched = True
                    matched_count += 1
                    if bin_clean and not matched_comp.bin:
                        matched_comp.bin = bin_clean
                        matched_comp.save(update_fields=['bin'])
                else:
                    unmatched_count += 1

                is_active = (status.strip().lower() != 'заблокирована')
                WebkassaCashRegister.objects.create(
                    is_active=is_active,
                    cto=cto_clean,
                    name=name,
                    serial_number=serial,
                    status=status,
                    ofd=ofd,
                    bin_iin=bin_clean or bin_raw,
                    organization=org,
                    expires_at=expires_date,
                    company=matched_comp,
                    auto_matched=auto_matched
                )
                created_count += 1

    return {
        'total': total_rows,
        'created': created_count,
        'updated': updated_count,
        'matched': matched_count,
        'unmatched': unmatched_count,
        'cto': cto_clean,
    }
