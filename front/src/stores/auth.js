import { defineStore } from 'pinia'
import { authApi } from '../api/auth'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    accessToken: localStorage.getItem('access_token') || null,
    refreshToken: localStorage.getItem('refresh_token') || null,
    loading: false,
  }),

  getters: {
    isAuthenticated: (state) => !!state.accessToken,
    isSuperAdmin: (state) => state.user?.role === 'SUPERADMIN',
    isManager: (state) => state.user?.role === 'MANAGER',
    isViewer: (state) => state.user?.role === 'VIEWER',
    canEdit: (state) => ['SUPERADMIN', 'MANAGER'].includes(state.user?.role),
    userDisplayName: (state) => state.user?.full_name || state.user?.username || 'Пользователь',
  },

  actions: {
    async login(username, password) {
      this.loading = true
      try {
        const res = await authApi.login(username, password)
        this.accessToken = res.data.access
        this.refreshToken = res.data.refresh
        this.user = res.data.user

        localStorage.setItem('access_token', this.accessToken)
        localStorage.setItem('refresh_token', this.refreshToken)
        localStorage.setItem('user', JSON.stringify(this.user))
        return { success: true }
      } catch (err) {
        const errorMsg = err.response?.data?.detail ||
                         err.response?.data?.non_field_errors?.[0] ||
                         'Ошибка входа в систему'
        return { success: false, error: errorMsg }
      } finally {
        this.loading = false
      }
    },

    async register(data) {
      this.loading = true
      try {
        const res = await authApi.register(data)
        return { success: true, message: res.data.message }
      } catch (err) {
        let errorMsg = 'Ошибка при регистрации'
        if (err.response?.data) {
          const firstKey = Object.keys(err.response.data)[0]
          const val = err.response.data[firstKey]
          errorMsg = Array.isArray(val) ? `${firstKey}: ${val[0]}` : String(val)
        }
        return { success: false, error: errorMsg }
      } finally {
        this.loading = false
      }
    },

    async fetchMe() {
      if (!this.accessToken) return
      try {
        const res = await authApi.getMe()
        this.user = res.data
        localStorage.setItem('user', JSON.stringify(this.user))
      } catch (err) {
        this.logout()
      }
    },

    logout() {
      this.user = null
      this.accessToken = null
      this.refreshToken = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    },
  },
})
