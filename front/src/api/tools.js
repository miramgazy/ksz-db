import client from './client'

export const toolsApi = {
  generatePassword(params = {}) {
    return client.get('/tools/generate-password/', { params })
  },
  getStats() {
    return client.get('/tools/stats/')
  },
}
