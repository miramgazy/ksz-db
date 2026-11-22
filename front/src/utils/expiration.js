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
    return 'bg-emerald-100 text-emerald-900 border-emerald-300'
  }
  if (days > 30) {
    // 🟢 Green (> 30 days)
    return 'bg-emerald-100 text-emerald-900 border-emerald-300'
  }
  if (days >= 8 && days <= 30) {
    // 🟡 Yellow / Amber (8–30 days)
    return 'bg-amber-100 text-amber-900 border-amber-300 font-semibold'
  }
  if (days >= 1 && days <= 7) {
    // 🟠 Orange (1–7 days)
    return 'bg-orange-100 text-orange-950 border-orange-400 font-extrabold shadow-xs'
  }
  if (days === 0) {
    // 🟤 Dark Amber / Today
    return 'bg-amber-200 text-amber-950 border-amber-500 font-extrabold animate-pulse shadow-xs'
  }
  // 🔴 Red / Expired (< 0 days)
  return 'bg-rose-100 text-rose-950 border-rose-400 font-extrabold shadow-xs'
}

export const getExpirationTextClass = (days, isIts = true) => {
  if (!isIts) {
    return 'text-slate-900 hover:text-blue-600 font-bold'
  }
  if (days === null || days === undefined || days > 30) {
    return 'text-emerald-950 hover:text-emerald-700 font-extrabold'
  }
  if (days >= 8 && days <= 30) {
    return 'text-amber-950 hover:text-amber-700 font-extrabold'
  }
  if (days >= 1 && days <= 7) {
    return 'text-orange-950 hover:text-orange-700 font-extrabold'
  }
  if (days === 0) {
    return 'text-amber-950 hover:text-amber-700 font-extrabold'
  }
  return 'text-rose-950 hover:text-rose-700 font-extrabold'
}

export const getExpirationIcon = (days) => {
  if (days === null || days === undefined || days > 30) {
    return 'pi pi-shield text-emerald-700'
  }
  if (days >= 8 && days <= 30) {
    return 'pi pi-clock text-amber-700'
  }
  if (days >= 1 && days <= 7) {
    return 'pi pi-exclamation-circle text-orange-700'
  }
  if (days === 0) {
    return 'pi pi-exclamation-triangle text-amber-900'
  }
  return 'pi pi-times-circle text-rose-700'
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
    return '!bg-emerald-50/50 !border-emerald-300'
  }
  if (days >= 8 && days <= 30) {
    return '!bg-amber-50/50 !border-amber-300'
  }
  if (days >= 1 && days <= 7) {
    return '!bg-orange-50/50 !border-orange-300'
  }
  if (days === 0) {
    return '!bg-amber-100/60 !border-amber-400'
  }
  return '!bg-rose-50/60 !border-rose-300'
}
