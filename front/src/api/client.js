import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to attach JWT token
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}, (error) => {
  return Promise.reject(error)
})

// Response interceptor to handle token expiry
client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // Don't intercept or loop if request was for auth endpoints
    const isAuthRequest = originalRequest?.url?.includes('/auth/')
    if (isAuthRequest) {
      return Promise.reject(error)
    }

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      const refreshToken = localStorage.getItem('refresh_token')

      if (refreshToken) {
        try {
          const res = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
            refresh: refreshToken,
          })
          const newAccess = res.data.access
          localStorage.setItem('access_token', newAccess)
          originalRequest.headers.Authorization = `Bearer ${newAccess}`
          return client(originalRequest)
        } catch (refreshErr) {
          // Token refresh failed, clear and logout
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('user')
          if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
            window.location.href = '/login'
          }
        }
      } else {
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')
        if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(error)
  }
)

export default client
