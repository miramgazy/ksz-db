import client from './client'

export const licenceTypesApi = {
  getLicenceTypes(params = {}) {
    return client.get('/licence-types/', { params })
  },
  createLicenceType(data) {
    return client.post('/licence-types/', data)
  },
  updateLicenceType(id, data) {
    return client.patch(`/licence-types/${id}/`, data)
  },
  deleteLicenceType(id) {
    return client.delete(`/licence-types/${id}/`)
  },
}
