/**
 * Expiration dates, remaining days calculation and visual color gradation utilities
 * Used across CompanyListView, ItsServicesView, and CompanyDetailDrawer
 */

export const getDaysRemaining = (expiresAt, fallbackDays = null) => {
  if (fallbackDays !== null && fallbackDays !== undefined) {
    return fallbackDays
  }
  if (!expiresAt) return null
  const target = new Date(expiresAt)
  const today = new Date()
  target.setHours(0, 0, 0, 0)
  today.setHours(0, 0, 0, 0)
  return Math.round((target - today) / (1000 * 60 * 60 * 24))
}

export const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  const d = new Date(dateStr)
  return d.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

export const formatDaysRemaining = (days) => {
  if (days === null || days === undefined) return ''
  if (days < 0) return `просрочен на ${Math.abs(days)} дн.`
  if (days === 0) return 'сегодня'
  if (days === 1) return 'завтра'
  return `ещё ${days} дн.`
}

export const getExpirationBadgeClass = (days) => {
  if (days === null || days === undefined) {
    return 'bg-emerald-100 text-emerald-900 border-emerald-300 dark:bg-emerald-950/80 dark:text-emerald-300 dark:border-emerald-700'
  }
  if (days > 30) {
    // 🟢 Green (> 30 days)
    return 'bg-emerald-100 text-emerald-900 border-emerald-300 dark:bg-emerald-950/80 dark:text-emerald-300 dark:border-emerald-700'
  }
  if (days >= 8 && days <= 30) {
    // 🟡 Yellow / Amber (8–30 days)
    return 'bg-amber-100 text-amber-900 border-amber-300 font-semibold dark:bg-amber-950/80 dark:text-amber-300 dark:border-amber-700'
  }
  if (days >= 1 && days <= 7) {
    // 🟠 Orange (1–7 days)
    return 'bg-orange-100 text-orange-950 border-orange-400 font-extrabold shadow-xs dark:bg-orange-950/80 dark:text-orange-300 dark:border-orange-700'
  }
  if (days === 0) {
    // 🟤 Dark Amber / Today
    return 'bg-amber-200 text-amber-950 border-amber-500 font-extrabold animate-pulse shadow-xs dark:bg-amber-900/90 dark:text-amber-200 dark:border-amber-600'
  }
  // 🔴 Red / Expired (< 0 days)
  return 'bg-rose-100 text-rose-950 border-rose-400 font-extrabold shadow-xs dark:bg-rose-950/80 dark:text-rose-300 dark:border-rose-700'
}

export const getExpirationTextClass = (days, isIts = true) => {
  if (!isIts) {
    return 'text-slate-900 dark:text-slate-100 hover:text-blue-600 dark:hover:text-blue-400 font-bold'
  }
  if (days === null || days === undefined || days > 30) {
    return 'text-emerald-950 dark:text-emerald-300 hover:text-emerald-700 dark:hover:text-emerald-200 font-extrabold'
  }
  if (days >= 8 && days <= 30) {
    return 'text-amber-950 dark:text-amber-300 hover:text-amber-700 dark:hover:text-amber-200 font-extrabold'
  }
  if (days >= 1 && days <= 7) {
    return 'text-orange-950 dark:text-orange-300 hover:text-orange-700 dark:hover:text-orange-200 font-extrabold'
  }
  if (days === 0) {
    return 'text-amber-950 dark:text-amber-300 hover:text-amber-700 dark:hover:text-amber-200 font-extrabold'
  }
  return 'text-rose-950 dark:text-rose-300 hover:text-rose-700 dark:hover:text-rose-200 font-extrabold'
}

export const getExpirationIcon = (days) => {
  if (days === null || days === undefined || days > 30) {
    return 'pi pi-shield text-emerald-700 dark:text-emerald-400'
  }
  if (days >= 8 && days <= 30) {
    return 'pi pi-clock text-amber-700 dark:text-amber-400'
  }
  if (days >= 1 && days <= 7) {
    return 'pi pi-exclamation-circle text-orange-700 dark:text-orange-400'
  }
  if (days === 0) {
    return 'pi pi-exclamation-triangle text-amber-900 dark:text-amber-300'
  }
  return 'pi pi-times-circle text-rose-700 dark:text-rose-400'
}

export const getItsTooltip = (data) => {
  if (!data) return 'ИТС'
  const days = data.its_days_remaining ?? getDaysRemaining(data.its_expires_at)
  if (!data.its_expires_at) {
    return 'ИТС: Подключено'
  }
  const dateFormatted = formatDate(data.its_expires_at)
  if (days === null || days === undefined) {
    return `ИТС до ${dateFormatted}`
  }
  if (days < 0) {
    return `ИТС: просрочен на ${Math.abs(days)} дн. (до ${dateFormatted})`
  }
  if (days === 0) {
    return `ИТС: истекает сегодня (${dateFormatted})`
  }
  return `ИТС до ${dateFormatted} (ещё ${days} дн.)`
}

export const getExpirationDrawerBg = (days) => {
  if (days === null || days === undefined || days > 30) {
    return '!bg-emerald-50/50 !border-emerald-300 dark:!bg-emerald-950/40 dark:!border-emerald-800'
  }
  if (days >= 8 && days <= 30) {
    return '!bg-amber-50/50 !border-amber-300 dark:!bg-amber-950/40 dark:!border-amber-800'
  }
  if (days >= 1 && days <= 7) {
    return '!bg-orange-50/50 !border-orange-300 dark:!bg-orange-950/40 dark:!border-orange-800'
  }
  if (days === 0) {
    return '!bg-amber-100/60 !border-amber-400 dark:!bg-amber-950/50 dark:!border-amber-700'
  }
  return '!bg-rose-50/60 !border-rose-300 dark:!bg-rose-950/40 dark:!border-rose-800'
}

export const DEFAULT_KEY_LICENSE_MODULES = [
  'ChainOperations (Chain)',
  'RMS (Front Fast Food)',
]

export const getKeyLicenseModules = () => {
  try {
    const raw = localStorage.getItem('ksz_key_license_modules')
    if (raw) {
      const parsed = JSON.parse(raw)
      if (Array.isArray(parsed) && parsed.length > 0) {
        return parsed
      }
    }
  } catch (e) {}
  return [...DEFAULT_KEY_LICENSE_MODULES]
}

export const setKeyLicenseModules = (modules) => {
  try {
    localStorage.setItem('ksz_key_license_modules', JSON.stringify(modules))
  } catch (e) {}
}

/**
 * Рассчитывает эффективный срок и статус лицензии заведения по списку приоритетных модулей.
 * Приоритет по умолчанию:
 * 1. ChainOperations (Chain)
 * 2. RMS (Front Fast Food)
 * 3. Общий срок из заголовка лога (expiration)
 */
export const getEffectiveLicenseInfo = (company, customKeyModules = null) => {
  if (!company) {
    return {
      status: 'none',
      date: null,
      source: null,
      isPermanent: false,
      daysRemaining: null,
      error: null
    }
  }

  if (company.last_license_error) {
    return {
      status: 'error',
      date: null,
      source: null,
      isPermanent: false,
      daysRemaining: null,
      error: company.last_license_error
    }
  }

  const lic = company.license_data
  if (!lic || typeof lic !== 'object') {
    return {
      status: 'none',
      date: null,
      source: null,
      isPermanent: false,
      daysRemaining: null,
      error: null
    }
  }

  const keyModules = customKeyModules || getKeyLicenseModules()
  const modules = Array.isArray(lic.modules) ? lic.modules : []

  // Ищем первый совпавший приоритетный модуль
  let matchedModule = null
  for (const keyName of keyModules) {
    if (!keyName) continue
    const found = modules.find(m => m.name && m.name.trim().toLowerCase() === keyName.trim().toLowerCase())
    if (found) {
      matchedModule = found
      break
    }
  }

  let effectiveDate = null
  let isPermanent = false
  let source = null

  if (matchedModule) {
    source = matchedModule.name
    if (matchedModule.to) {
      effectiveDate = matchedModule.to
    } else {
      isPermanent = true
    }
  } else if (lic.expiration) {
    effectiveDate = lic.expiration
    source = 'Общий срок'
  } else if (modules.length > 0) {
    isPermanent = true
    source = 'Модули'
  } else {
    return {
      status: 'none',
      date: null,
      source: null,
      isPermanent: false,
      daysRemaining: null,
      error: null
    }
  }

  if (isPermanent) {
    return {
      status: 'active',
      date: null,
      source,
      isPermanent: true,
      daysRemaining: null,
      error: null
    }
  }

  if (!effectiveDate) {
    return {
      status: 'none',
      date: null,
      source,
      isPermanent: false,
      daysRemaining: null,
      error: null
    }
  }

  const target = new Date(effectiveDate)
  if (isNaN(target.getTime())) {
    return {
      status: 'none',
      date: effectiveDate,
      source,
      isPermanent: false,
      daysRemaining: null,
      error: null
    }
  }

  const today = new Date()
  today.setHours(0, 0, 0, 0)
  target.setHours(0, 0, 0, 0)

  const daysRemaining = Math.round((target - today) / (1000 * 60 * 60 * 24))
  const status = daysRemaining >= 0 ? 'active' : 'expired'

  return {
    status,
    date: effectiveDate,
    source,
    isPermanent: false,
    daysRemaining,
    error: null
  }
}

export const getLicenseStatus = (company) => {
  return getEffectiveLicenseInfo(company).status
}

export const getLicenseIconClass = (company) => {
  const info = getEffectiveLicenseInfo(company)
  if (info.status === 'error' || company?.last_license_error) {
    return '!text-red-500 hover:!bg-red-50 dark:!text-red-400 dark:hover:!bg-red-950/40'
  }
  if (info.status === 'active') {
    return '!text-emerald-500 hover:!bg-emerald-50 dark:!text-emerald-400 dark:hover:!bg-emerald-950/40'
  }
  if (info.status === 'expired') {
    return '!text-amber-500 hover:!bg-amber-50 dark:!text-amber-400 dark:hover:!bg-amber-950/40'
  }
  return '!text-slate-400 hover:!bg-slate-100 dark:!text-slate-500 dark:hover:!bg-slate-800'
}

export const getLicenseSeverity = (company) => {
  const info = getEffectiveLicenseInfo(company)
  if (info.status === 'error') return 'danger'
  if (info.status === 'active') return 'success'
  if (info.status === 'expired') return 'warn'
  return 'secondary'
}

export const getLicenseTooltip = (company) => {
  const info = getEffectiveLicenseInfo(company)
  if (info.error || company?.last_license_error) {
    return `Текущие лицензии: ошибка обновления (${info.error || company.last_license_error})`
  }
  const sourcePart = info.source ? ` • ${info.source}` : ''
  if (info.status === 'active') {
    if (info.isPermanent) {
      return `Текущие лицензии: активна (бессрочная${sourcePart})`
    }
    return `Текущие лицензии: активна (до ${info.date}${sourcePart})`
  }
  if (info.status === 'expired') {
    return `Текущие лицензии: срок истек (до ${info.date}${sourcePart})`
  }
  return 'Текущие лицензии: нет данных (нажмите для просмотра)'
}

/**
 * WebKassa cash register badge styling and tooltips for CompanyListView
 */
export const getWebkassaBadgeClass = (days) => {
  if (days === null || days === undefined || days > 15) {
    // 🌐 Sky Blue (> 15 days)
    return 'bg-sky-50 text-sky-700 border-sky-300 dark:bg-sky-950/80 dark:text-sky-300 dark:border-sky-700'
  }
  if (days >= 8 && days <= 15) {
    // 🔵 Blue (8–15 days)
    return 'bg-blue-100 text-blue-900 border-blue-300 font-semibold dark:bg-blue-950/80 dark:text-blue-300 dark:border-blue-700'
  }
  if (days >= 4 && days <= 7) {
    // 🟡 Amber / Yellow (4–7 days)
    return 'bg-amber-100 text-amber-900 border-amber-300 font-semibold dark:bg-amber-950/80 dark:text-amber-300 dark:border-amber-700'
  }
  if (days >= 2 && days <= 3) {
    // 🟠 Orange (2–3 days)
    return 'bg-orange-100 text-orange-950 border-orange-400 font-extrabold shadow-xs dark:bg-orange-950/80 dark:text-orange-300 dark:border-orange-700'
  }
  if (days >= 0 && days <= 1) {
    // 🔴 Red / 1 day (0–1 day)
    return 'bg-red-100 text-red-950 border-red-400 font-extrabold shadow-xs dark:bg-red-950/80 dark:text-red-300 dark:border-red-700'
  }
  // 🔴 Rose / Expired (< 0 days)
  return 'bg-rose-100 text-rose-950 border-rose-400 font-extrabold shadow-xs dark:bg-rose-950/80 dark:text-rose-300 dark:border-rose-700'
}

export const getWebkassaIconClass = (days) => {
  if (days === null || days === undefined || days > 15) {
    return 'text-sky-600 dark:text-sky-400'
  }
  if (days >= 8 && days <= 15) {
    return 'text-blue-600 dark:text-blue-400'
  }
  if (days >= 4 && days <= 7) {
    return 'text-amber-600 dark:text-amber-400'
  }
  if (days >= 2 && days <= 3) {
    return 'text-orange-600 dark:text-orange-400'
  }
  if (days >= 0 && days <= 1) {
    return 'text-red-600 dark:text-red-400'
  }
  return 'text-rose-600 dark:text-rose-400'
}

export const getWebkassaTooltip = (data) => {
  if (!data || !data.webkassa_count) return 'WebKassa'
  const count = data.webkassa_count
  const days = data.webkassa_days_remaining
  const regs = data.webkassa_registers || []

  if (count === 1 && regs.length === 1) {
    const reg = regs[0]
    const dateStr = reg.expires_at ? formatDate(reg.expires_at) : 'без срока'
    const daysText = reg.days_remaining !== null && reg.days_remaining !== undefined
      ? ` (${formatDaysRemaining(reg.days_remaining)})`
      : ''
    return `WebKassa: ${reg.serial_number} (${reg.name || 'Касса'})\nСрок: ${dateStr}${daysText}\nОФД: ${reg.ofd || '—'} [${reg.status || '—'}]`
  }

  const dateFormatted = data.webkassa_expires_at ? formatDate(data.webkassa_expires_at) : '—'
  const daysText = days !== null && days !== undefined ? ` (${formatDaysRemaining(days)})` : ''
  let title = `WebKassa (${count} касс)\nБлижайшее окончание: ${dateFormatted}${daysText}`
  if (regs.length > 0) {
    title += '\n' + regs.map(r => `• ${r.serial_number} (${r.name}): до ${r.expires_at ? formatDate(r.expires_at) : '—'}`).join('\n')
  }
  return title
}
