import re

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
    """
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
    (e.g. '9.5.6-RMS', '9.5.8-Chain', or '9.5.6').
    Uses an in-memory cache of distributions for high-speed batch resolution.
    """
    global _dist_cache
    if not iiko_version:
        return ''

    from .models import IikoDistribution

    if _dist_cache is None:
        cache = {}
        for d in IikoDistribution.objects.all():
            v_clean = clean_iiko_version(d.iiko_version)
            t_clean = (d.type or '').strip().upper()
            if d.link_ya:
                cache[(v_clean, t_clean)] = d.link_ya.strip()
                if v_clean not in cache:
                    cache[v_clean] = d.link_ya.strip()
        _dist_cache = cache

    parts = str(iiko_version).split('-')
    ver = clean_iiko_version(parts[0].strip())
    dist_type = parts[1].strip().upper() if len(parts) > 1 else ''

    if dist_type and (ver, dist_type) in _dist_cache:
        return _dist_cache[(ver, dist_type)]
    if node_type and (ver, str(node_type).upper()) in _dist_cache:
        return _dist_cache[(ver, str(node_type).upper())]
    if ver in _dist_cache:
        return _dist_cache[ver]

    return ''
