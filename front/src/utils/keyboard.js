/**
 * Keyboard Layout & Kazakh/Russian Normalization Utility
 * Supports bilingual search (QWERTY <-> JCUKEN) and Kazakh specific letter normalization.
 */

// Mapping QWERTY (EN) -> JCUKEN (RU/KZ)
const EN_TO_RU = {
  // Lowercase
  'q': 'й', 'w': 'ц', 'e': 'у', 'r': 'к', 't': 'е', 'y': 'н', 'u': 'г', 'i': 'ш', 'o': 'щ', 'p': 'з',
  '[': 'х', ']': 'ъ', 'a': 'ф', 's': 'ы', 'd': 'в', 'f': 'а', 'g': 'п', 'h': 'р', 'j': 'о', 'k': 'л',
  'l': 'д', ';': 'ж', "'": 'э', 'z': 'я', 'x': 'ч', 'c': 'с', 'v': 'м', 'b': 'и', 'n': 'т', 'm': 'ь',
  ',': 'б', '.': 'ю', '/': '.', '`': 'ё',
  // Uppercase
  'Q': 'Й', 'W': 'Ц', 'E': 'У', 'R': 'К', 'T': 'Е', 'Y': 'Н', 'U': 'Г', 'I': 'Ш', 'O': 'Щ', 'P': 'З',
  '{': 'Х', '}': 'Ъ', 'A': 'Ф', 'S': 'Ы', 'D': 'В', 'F': 'А', 'G': 'П', 'H': 'Р', 'J': 'О', 'K': 'Л',
  'L': 'Д', ':': 'Ж', '"': 'Э', 'Z': 'Я', 'X': 'Ч', 'C': 'С', 'V': 'М', 'B': 'И', 'N': 'Т', 'M': 'Ь',
  '<': 'Б', '>': 'Ю', '?': ',', '~': 'Ё',
  // Shift symbols
  '@': '"', '#': '№', '$': ';', '^': ':', '&': '?'
}

// Reverse mapping RU -> EN
const RU_TO_EN = {}
for (const [en, ru] of Object.entries(EN_TO_RU)) {
  RU_TO_EN[ru] = en
}

// Kazakh keyboard layout on number row:
// In Kazakh Cyrillic layout, numbers 2-0 produce: ә, і, ң, ғ, ү, ұ, қ, ө, һ
const KZ_NUMBER_TO_CHAR = {
  '2': 'ә', '3': 'і', '4': 'ң', '5': 'ғ', '6': 'ү', '7': 'ұ', '8': 'қ', '9': 'ө', '0': 'һ',
  '@': 'Ә', '#': 'І', '$': 'Ң', '%': 'Ғ', '^': 'Ү', '&': 'Ұ', '*': 'Қ', '(': 'Ө', ')': 'Һ'
}
const CHAR_TO_KZ_NUMBER = {}
for (const [k, v] of Object.entries(KZ_NUMBER_TO_CHAR)) {
  CHAR_TO_KZ_NUMBER[v] = k
}

// Kazakh to Russian phonetic equivalence (e.g. Қ <-> К, Ә <-> А, Ө <-> О, etc.)
const KZ_TO_RU_NORMAL = {
  'ә': 'а', 'Ә': 'А',
  'і': 'и', 'І': 'И',
  'ң': 'н', 'Ң': 'Н',
  'ғ': 'г', 'Ғ': 'Г',
  'ү': 'у', 'Ү': 'У',
  'ұ': 'у', 'Ұ': 'У',
  'қ': 'к', 'Қ': 'К',
  'ө': 'о', 'Ө': 'О',
  'һ': 'х', 'Һ': 'Х'
}

/**
 * Normalizes Kazakh characters to their Russian Cyrillic phonetic equivalents.
 * Example: 'Ақтөбе' -> 'Актобе', 'Қызылорда' -> 'Кызылорда'
 */
export function normalizeKazakh(text) {
  if (!text) return ''
  return text.split('').map(ch => KZ_TO_RU_NORMAL[ch] || ch).join('')
}

/**
 * Switches keyboard layout between English and Russian/Kazakh.
 * E.g.: 'Ehfkmcr' -> 'Уральск', 'Ыфьфд' -> 'Samal', 'Frnjwt' -> 'Актобе'
 */
export function switchKeyboardLayout(text) {
  if (!text) return ''

  // Determine primary direction based on characters
  let hasLatin = false
  let hasCyrillic = false

  for (const ch of text) {
    if (/[a-zA-Z]/.test(ch)) hasLatin = true
    if (/[а-яА-ЯёЁәіңғүұқөһӘІҢҒҮҰҚӨҺ]/.test(ch)) hasCyrillic = true
  }

  // If text is primarily Latin, convert to Cyrillic
  if (hasLatin && !hasCyrillic) {
    return text.split('').map(ch => EN_TO_RU[ch] || KZ_NUMBER_TO_CHAR[ch] || ch).join('')
  }

  // If text is primarily Cyrillic, convert to Latin
  if (hasCyrillic) {
    return text.split('').map(ch => RU_TO_EN[ch] || CHAR_TO_KZ_NUMBER[ch] || ch).join('')
  }

  // Mixed or neutral: map what we can
  return text.split('').map(ch => EN_TO_RU[ch] || RU_TO_EN[ch] || ch).join('')
}

/**
 * Returns a list of search query variants for smart dual search:
 * 1. Original query
 * 2. Switched keyboard layout variant
 * 3. Kazakh-normalized original
 * 4. Kazakh-normalized switched
 */
export function getSearchVariants(query) {
  if (!query || typeof query !== 'string') return []
  const trimmed = query.trim()
  if (!trimmed) return []

  const variants = new Set()
  const lowerOriginal = trimmed.toLowerCase()
  variants.add(lowerOriginal)

  // 1. Switched layout
  const switched = switchKeyboardLayout(trimmed).toLowerCase()
  if (switched && switched !== lowerOriginal) {
    variants.add(switched)
  }

  // 2. Normalized Kazakh for original
  const normOriginal = normalizeKazakh(lowerOriginal)
  if (normOriginal && normOriginal !== lowerOriginal) {
    variants.add(normOriginal)
  }

  // 3. Normalized Kazakh for switched
  if (switched) {
    const normSwitched = normalizeKazakh(switched)
    if (normSwitched && normSwitched !== switched) {
      variants.add(normSwitched)
    }
  }

  return Array.from(variants)
}

/**
 * Checks whether target text matches the search query under smart dual search rules.
 * Matches if any search variant is found in the target or in the normalized target.
 */
export function matchesSmartSearch(targetText, query) {
  if (!query) return true
  if (!targetText) return false

  const targetStr = String(targetText).toLowerCase()
  const normTarget = normalizeKazakh(targetStr)
  const variants = getSearchVariants(query)

  for (const v of variants) {
    if (targetStr.includes(v) || normTarget.includes(v)) {
      return true
    }
  }

  return false
}
