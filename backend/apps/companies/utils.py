import re
from typing import Tuple


def clean_iiko_version(v: str) -> str:
    """
    Cleans up Excel-mangled iiko versions back to human-readable semantic versions.
    Strips redundant node-type suffixes (-RMS, -Chain, etc.).
    For example:
        '09.05.2007' -> '9.5.7'
        '07.02.2008' -> '7.2.8'
        '08.06.2009' -> '8.6.9'
        '09.05.2007-RMS' -> '9.5.7'
        '09.05.2007-Chain' -> '9.5.7'
        '9.5.7-RMS' -> '9.5.7'
        '9.5.8 - Chain' -> '9.5.8'
        '9.5.7' -> '9.5.7'
        '8.0.6' -> '8.0.6'
        '9.6.8035.0' -> '9.6.8035.0' (preserved, not mangled!)
    """
    if not v:
        return ''
    v = str(v).strip()
    m = re.match(r'^(\d{1,2})[./](\d{1,2})[./](\d{4})(.*)$', v)
    if m:
        major = int(m.group(1))
        minor = int(m.group(2))
        year = int(m.group(3))
        # Only treat as Excel date if year is within 2000-2099 (e.g. 2006, 2007, 2008, 2009)
        # iiko build numbers like 8035 or 7012 are NOT Excel years!
        if 2000 <= year <= 2099:
            patch = year - 2000
            extra = m.group(4) or ''
            v = f"{major}.{minor}.{patch}{extra}"
    v = re.sub(r'[\s\-_/]+(RMS|Chain|Chains|РМС|Чейн)$', '', v, flags=re.IGNORECASE).strip()
    v = v.strip(' -_/')
    return v


def extract_base_iiko_version(v: str) -> str:
    """
    Извлекает базовую версию iiko (Major.Minor.Patch) из полной версии сборки.
    Например:
        '9.6.8035.0' -> '9.6.8'
        '9.5.8011.0' -> '9.5.8'
        '8.6.9015.0' -> '8.6.9'
        '8.0.6012.0' -> '8.0.6'
        '7.2.8005.0' -> '7.2.8'
        '9.6.8'      -> '9.6.8'
        '9.6.8-RMS'  -> '9.6.8'
    """
    if not v:
        return ''
    cleaned = clean_iiko_version(v)
    parts = str(cleaned).split('-')
    raw = parts[0].strip()

    # Формат 4 сегмента: 9.6.8035.0 -> 9.6.8
    m4 = re.match(r'^(\d+)\.(\d+)\.(\d)\d+(?:\..*)?$', raw)
    if m4:
        return f"{m4.group(1)}.{m4.group(2)}.{m4.group(3)}"

    # Стандартный формат 3 сегмента: 9.6.8
    m3 = re.match(r'^(\d+)\.(\d+)\.(\d+)(?:-.*)?$', raw)
    if m3:
        return f"{m3.group(1)}.{m3.group(2)}.{m3.group(3)}"

    return raw


def version_sort_key(v: str):
    """
    Sort key for semantic version comparison (e.g. 9.6.8 > 9.5.7 > 8.0.6).
    Returns a tuple of numeric parts followed by any trailing suffix.
    """
    if not v:
        return ([], '')
    v_clean = clean_iiko_version(v)
    parts = re.split(r'[-_\s]', str(v_clean).strip())
    nums = []
    for p in parts[0].split('.'):
        try:
            nums.append(int(p))
        except ValueError:
            nums.append(0)
    extra = parts[1] if len(parts) > 1 else ''
    return (nums, extra)


_dist_cache = None

def invalidate_distribution_cache():
    global _dist_cache
    _dist_cache = None


def get_distribution_link(iiko_version: str, node_type: str = '') -> str:
    """
    Finds the Yandex Disk distribution download link for a given iiko_version string
    (e.g. '9.6.8035.0', '9.5.6-RMS', '9.5.8-Chain', or '9.5.6').
    Supports two-way fallback between full build versions (9.6.8035.0) and base versions (9.6.8).
    """
    global _dist_cache
    if not iiko_version:
        return ''

    from .models import IikoDistribution

    if _dist_cache is None:
        cache = {}
        for d in IikoDistribution.objects.all():
            v_clean = clean_iiko_version(d.iiko_version)
            v_base = extract_base_iiko_version(v_clean)
            t_clean = (d.type or '').strip().upper()
            link = (d.link_ya or '').strip()
            if link:
                cache[(v_clean, t_clean)] = link
                if v_clean not in cache:
                    cache[v_clean] = link
                if v_base:
                    if (v_base, t_clean) not in cache:
                        cache[(v_base, t_clean)] = link
                    if v_base not in cache:
                        cache[v_base] = link
        _dist_cache = cache

    parts = str(iiko_version).split('-')
    ver = clean_iiko_version(parts[0].strip())
    ver_base = extract_base_iiko_version(ver)
    dist_type = parts[1].strip().upper() if len(parts) > 1 else ''
    node_t = str(node_type).strip().upper() if node_type else ''

    # 1. Exact version match
    if dist_type and (ver, dist_type) in _dist_cache:
        return _dist_cache[(ver, dist_type)]
    if node_t and (ver, node_t) in _dist_cache:
        return _dist_cache[(ver, node_t)]
    if ver in _dist_cache:
        return _dist_cache[ver]

    # 2. Base version match fallback (e.g. 9.6.8 for 9.6.8035.0 or vice versa)
    if ver_base:
        if dist_type and (ver_base, dist_type) in _dist_cache:
            return _dist_cache[(ver_base, dist_type)]
        if node_t and (ver_base, node_t) in _dist_cache:
            return _dist_cache[(ver_base, node_t)]
        if ver_base in _dist_cache:
            return _dist_cache[ver_base]

    return ''


def cascade_update_company_versions(base_ver: str, new_ver: str) -> int:
    """
    Каскадно обновляет все заведения со старой базовой версией (например 9.6.8)
    на новую полную версию (например 9.6.8035.0).
    """
    if not base_ver or not new_ver or base_ver == new_ver:
        return 0

    from .models import Company

    updated_count = 0
    updated_count += Company.objects.filter(iiko_version=base_ver).update(iiko_version=new_ver)
    updated_count += Company.objects.filter(iiko_version__startswith=f"{base_ver}-").update(iiko_version=new_ver)
    updated_count += Company.objects.filter(iiko_version__startswith=f"{base_ver} ").update(iiko_version=new_ver)
    return updated_count


def sync_iiko_version_with_distributions(raw_version: str, node_type: str = 'RMS') -> Tuple[str, bool]:
    """
    Синхронизирует версию из лицензии с таблицей дистрибутивов IikoDistribution:
    1. Ищет точное совпадение (например 9.6.8035.0).
       Если найдено и есть заведения с базовой версией (например 9.6.8), каскадно обновляет их.
    2. Если точного нет, вычисляет базовую версию (например 9.6.8) и ищет в таблице.
       Если найдена старая версия (9.6.8) - заменяет её на 9.6.8035.0, сохраняя ссылку,
       и каскадно обновляет все заведения с этой базовой версией!
    3. Если версия вообще не найдена в базе - создаёт новые строки в IikoDistribution с пустой ссылкой.
    Возвращает (актуальная_версия, is_new_version)
    """
    if not raw_version:
        return ('', False)

    from .models import IikoDistribution

    ver = clean_iiko_version(raw_version)
    base_ver = extract_base_iiko_version(ver)
    type_str = 'Chain' if str(node_type).upper() == 'CHAIN' else 'RMS'

    # 1. Точное совпадение в таблице дистрибутивов
    dists_exact = IikoDistribution.objects.filter(iiko_version=ver)
    if dists_exact.exists():
        if base_ver and base_ver != ver:
            cascade_update_company_versions(base_ver, ver)
        return (ver, False)

    # 2. Поиск по базовой версии (например 9.6.8) и замена на полную версию 9.6.8035.0
    if base_ver and base_ver != ver:
        dists_base = IikoDistribution.objects.filter(iiko_version=base_ver)
        if dists_base.exists():
            dists_base.update(iiko_version=ver)
            cascade_update_company_versions(base_ver, ver)
            invalidate_distribution_cache()
            return (ver, False)

    # 3. Версия не найдена - создаём новую запись
    IikoDistribution.objects.create(iiko_version=ver, type=type_str, link_ya='')
    other_type = 'Chain' if type_str == 'RMS' else 'RMS'
    if not IikoDistribution.objects.filter(iiko_version=ver, type=other_type).exists():
        IikoDistribution.objects.create(iiko_version=ver, type=other_type, link_ya='')

    if base_ver and base_ver != ver:
        cascade_update_company_versions(base_ver, ver)

    invalidate_distribution_cache()
    return (ver, True)
