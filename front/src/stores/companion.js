import { defineStore } from 'pinia'
import { companionApi } from '../api/companion'
import { anydeskVersionsApi } from '../api/anydeskVersions'

export const useCompanionStore = defineStore('companion', {
  state: () => ({
    isOnline: false,
    details: null,
    lastChecked: null,
    profiles: [],
    preferredProfileId: parseInt(localStorage.getItem('ksz_preferred_anydesk_profile') || '0') || null,
  }),

  getters: {
    preferredProfile: (state) => {
      if (state.preferredProfileId && state.profiles.length) {
        const found = state.profiles.find(p => p.id === state.preferredProfileId)
        if (found) return found
      }
      return state.profiles.find(p => p.is_default) || state.profiles[0] || null
    },
  },

  actions: {
    async checkStatus() {
      if (!localStorage.getItem('access_token')) {
        this.isOnline = false
        this.details = null
        return false
      }
      const res = await companionApi.getStatus()
      this.isOnline = !!res.online
      this.details = res.data || null
      this.lastChecked = new Date()
      return this.isOnline
    },

    async loadProfiles() {
      try {
        const res = await anydeskVersionsApi.getVersions({ page_size: 100 })
        this.profiles = res.data.results || res.data
        return this.profiles
      } catch (e) {
        return []
      }
    },

    setPreferredProfile(id) {
      this.preferredProfileId = id
      if (id) {
        localStorage.setItem('ksz_preferred_anydesk_profile', id.toString())
      } else {
        localStorage.removeItem('ksz_preferred_anydesk_profile')
      }
    },

    async launchBackoffice({ server, port, login, password, clearbatUrl }) {
      if (this.isOnline) {
        try {
          const res = await companionApi.launchBackoffice({ server, port, login, password })
          return { success: true, via: 'helper', message: res.data.message }
        } catch (e) {
          // Fallback to browser protocol if helper fails
        }
      }

      // Browser URL protocol fallback
      if (clearbatUrl) {
        window.location.href = clearbatUrl
        return {
          success: true,
          via: 'protocol',
          message: 'Запрос на открытие отправлен через протокол clearbat://'
        }
      }
      return { success: false, message: 'Не удалось запустить BackOffice' }
    },

    async launchLicense({ company_id, server, port, login, password, place_name, licenseUrl }) {
      if (this.isOnline) {
        try {
          const res = await companionApi.launchLicense({
            company_id,
            server,
            port,
            login,
            password,
            place_name
          })
          return {
            success: true,
            via: 'helper',
            task_id: res.data?.task_id,
            message: res.data?.message || 'Команда передана агенту.'
          }
        } catch (e) {
          // Fallback to browser protocol if helper fails
        }
      }

      // Browser URL protocol fallback
      if (licenseUrl) {
        window.location.href = licenseUrl
        return {
          success: true,
          via: 'protocol',
          message: 'Запрос на обновление лицензии отправлен через протокол clearbat://'
        }
      }
      return { success: false, message: 'Не удалось запустить обновление лицензии' }
    },

    async pollLicenseTaskStatus(taskId, companyId, { maxAttempts = 3, intervalMs = 7000 } = {}) {
      if (!taskId) return { success: false, timeout: false, error: 'task_id отсутствует' }

      for (let attempt = 1; attempt <= maxAttempts; attempt++) {
        await new Promise(r => setTimeout(r, intervalMs))

        try {
          const res = await companionApi.getTaskStatus(taskId)
          const st = res.data?.status

          if (st === 'completed') {
            return { success: true, attempt, data: res.data }
          }
          if (st === 'error') {
            return {
              success: false,
              attempt,
              error: res.data?.error || 'Сервер iiko вернул ошибку при обновлении лицензии'
            }
          }
        } catch (e) {
          console.warn('[CompanionStore] Ошибка опроса статуса задачи:', e)
        }
      }

      return {
        success: false,
        timeout: true,
        error: 'Не удалось получить данные лицензии за 21 сек'
      }
    },

    async insertClearbat(payload) {
      await this.checkStatus()
      if (!this.isOnline) {
        return {
          success: false,
          message: 'Локальный агент не запущен на вашем рабочем месте. Запустите run_agent.bat для работы с базой ClearBat.'
        }
      }

      try {
        const res = await companionApi.insertClearbat(payload)
        return { success: true, message: res.data.message, revision: res.data.revision }
      } catch (err) {
        const msg = err.response?.data?.message || err.response?.data?.error || err.message || 'Ошибка записи в ClearBat'
        return { success: false, message: msg }
      }
    },

    async launchAnydesk({ anydesk_id, any_pass, profile = null }) {
      // Determine profile to use
      const activeProfile = profile || this.preferredProfile

      const payload = {
        anydesk_id,
        any_pass: any_pass || '',
        version_name: activeProfile?.name || 'Main Anydesk',
        is_sandbox: activeProfile?.is_sandbox || false,
        sandbox_params: activeProfile?.sandbox_params || '',
        exe_path: activeProfile?.exe_path || '',
      }

      if (this.isOnline) {
        try {
          const res = await companionApi.launchAnydesk(payload)
          return {
            success: true,
            via: 'helper',
            message: res.data.message,
            profile: activeProfile
          }
        } catch (e) {
          // Fallback to protocol
        }
      }

      // Fallback: Copy password to clipboard in browser if possible
      if (any_pass && navigator.clipboard) {
        try {
          await navigator.clipboard.writeText(any_pass)
        } catch (e) {}
      }

      // Protocol fallback
      window.location.href = `anydesk:${anydesk_id}`
      const modeDesc = activeProfile?.is_sandbox ? `(Sandboxie: ${activeProfile.sandbox_params})` : '(Обычный)'
      return {
        success: true,
        via: 'protocol',
        message: `AnyDesk ${anydesk_id} вызван через протокол ${modeDesc}. Пароль скопирован в буфер.`,
        profile: activeProfile
      }
    },
  },
})
