import client from './client'

export const anydeskVersionsApi = {
  getVersions(params = {}) {
    return client.get('/anydesk-versions/', { params })
  },
  createVersion(data) {
    return client.post('/anydesk-versions/', data)
  },
  updateVersion(id, data) {
    return client.patch(`/anydesk-versions/${id}/`, data)
  },
  deleteVersion(id) {
    return client.delete(`/anydesk-versions/${id}/`)
  },
}
