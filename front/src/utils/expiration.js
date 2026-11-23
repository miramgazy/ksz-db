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
