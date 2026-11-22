import client from './client'

export const distributionsApi = {
  getDistributions(params = {}) {
    return client.get('/iiko-distributions/', { params })
  },
  createDistribution(data) {
    return client.post('/iiko-distributions/', data)
  },
  updateDistribution(id, data) {
    return client.patch(`/iiko-distributions/${id}/`, data)
  },
  deleteDistribution(id) {
    return client.delete(`/iiko-distributions/${id}/`)
  },
  getVersions() {
    return client.get('/iiko-distributions/versions/')
  },
}
