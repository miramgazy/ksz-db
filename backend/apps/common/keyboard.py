"""
Keyboard layout & Kazakh/Russian phonetic normalization utility.
Handles QWERTY <-> JCUKEN layout switching and Kazakh letter equivalences.
"""

EN_TO_RU = {
    # Lowercase
    'q': 'й', 'w': 'ц', 'e': 'у', 'r': 'к', 't': 'е', 'y': 'н', 'u': 'г', 'i': 'ш', 'o': 'щ', 'p': 'з',
    '[': 'х', ']': 'ъ', 'a': 'ф', 's': 'ы', 'd': 'в', 'f': 'а', 'g': 'п', 'h': 'р', 'j': 'о', 'k': 'л',
    'l': 'д', ';': 'ж', "'": 'э', 'z': 'я', 'x': 'ч', 'c': 'с', 'v': 'м', 'b': 'и', 'n': 'т', 'm': 'ь',
    ',': 'б', '.': 'ю', '/': '.', '`': 'ё',
    # Uppercase
    'Q': 'Й', 'W': 'Ц', 'E': 'У', 'R': 'К', 'T': 'Е', 'Y': 'Н', 'U': 'Г', 'I': 'Ш', 'O': 'Щ', 'P': 'З',
    '{': 'Х', '}': 'Ъ', 'A': 'Ф', 'S': 'Ы', 'D': 'В', 'F': 'А', 'G': 'П', 'H': 'Р', 'J': 'О', 'K': 'Л',
    'L': 'Д', ':': 'Ж', '"': 'Э', 'Z': 'Я', 'X': 'Ч', 'C': 'С', 'V': 'М', 'B': 'И', 'N': 'Т', 'M': 'Ь',
    '<': 'Б', '>': 'Ю', '?': ',', '~': 'Ё',
    # Shift symbols
    '@': '"', '#': '№', '$': ';', '^': ':', '&': '?'
}

RU_TO_EN = {ru: en for en, ru in EN_TO_RU.items()}

# Kazakh keyboard layout on number row:
# 2-0: ә, і, ң, ғ, ү, ұ, қ, ө, һ
KZ_NUMBER_TO_CHAR = {
    '2': 'ә', '3': 'і', '4': 'ң', '5': 'ғ', '6': 'ү', '7': 'ұ', '8': 'қ', '9': 'ө', '0': 'һ',
    '@': 'Ә', '#': 'І', '$': 'Ң', '%': 'Ғ', '^': 'Ү', '&': 'Ұ', '*': 'Қ', '(': 'Ө', ')': 'Һ'
}
CHAR_TO_KZ_NUMBER = {v: k for k, v in KZ_NUMBER_TO_CHAR.items()}

KZ_TO_RU = {
    'ә': 'а', 'і': 'и', 'ң': 'н', 'ғ': 'г', 'ү': 'у', 'ұ': 'у', 'қ': 'к', 'ө': 'о', 'һ': 'х',
    'Ә': 'А', 'І': 'И', 'Ң': 'Н', 'Ғ': 'Г', 'Ү': 'У', 'Ұ': 'У', 'Қ': 'К', 'Ө': 'О', 'Һ': 'Х'
}


def normalize_kazakh(text: str) -> str:
    """Normalizes Kazakh letters to Russian Cyrillic equivalents (e.g. Қ -> К, Ә -> А)."""
    if not text:
        return ''
    return ''.join(KZ_TO_RU.get(c, c) for c in text)


def switch_keyboard_layout(text: str) -> str:
    """
    Switches text between English QWERTY and Russian/Kazakh Cyrillic.
    E.g. 'Ehfkmcr' -> 'Уральск', 'Ыфьфд' -> 'Samal', 'Frnj,t' -> 'Актобе'.
    """
    if not text:
        return ''

    has_latin = any('a' <= c.lower() <= 'z' for c in text)
    has_cyrillic = any('а' <= c.lower() <= 'я' or c.lower() in 'ёәіңғүұқөһ' for c in text)

    if has_latin and not has_cyrillic:
        return ''.join(EN_TO_RU.get(c, KZ_NUMBER_TO_CHAR.get(c, c)) for c in text)

    if has_cyrillic:
        # Normalize Kazakh specific characters that don't directly map to standard QWERTY
        normalized = ''.join(KZ_TO_RU.get(c, c) for c in text)
        return ''.join(RU_TO_EN.get(c, CHAR_TO_KZ_NUMBER.get(c, c)) for c in normalized)

    return ''.join(EN_TO_RU.get(c, RU_TO_EN.get(c, c)) for c in text)


def get_search_variants(query: str) -> list:
    """
    Returns unique non-empty search query variants:
    1. Original query
    2. Switched keyboard layout variant
    3. Kazakh-normalized original
    4. Kazakh-normalized switched
    5. Typical Kazakh/Russian equivalent substitutions (e.g. Актобе <-> Ақтөбе, Кызылорда <-> Қызылорда)
    """
    query = (query or '').strip()
    if not query:
        return []

    lower_query = query.lower()
    variants = {lower_query}

    # 1. Switched layout
    switched = switch_keyboard_layout(query).lower()
    if switched and switched != lower_query:
        variants.add(switched)

    # 2. Kazakh to Russian normalized
    norm = normalize_kazakh(lower_query)
    if norm and norm != lower_query:
        variants.add(norm)
        norm_switched = switch_keyboard_layout(norm).lower()
        if norm_switched:
            variants.add(norm_switched)

    # 3. If query contains typical Kazakh/Russian equivalent letters, add phonetic substitutes
    kz_substitutions = [
        ('к', 'қ'), ('қ', 'к'),
        ('о', 'ө'), ('ө', 'о'),
        ('а', 'ә'), ('ә', 'а'),
        ('г', 'ғ'), ('ғ', 'г'),
    ]
    for v in list(variants):
        for src, dst in kz_substitutions:
            if src in v:
                variants.add(v.replace(src, dst))

    return [v for v in variants if v]
