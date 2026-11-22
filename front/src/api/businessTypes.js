import client from './client'

export const businessTypesApi = {
  getBusinessTypes(params = {}) {
    return client.get('/business-types/', { params })
  },
  createBusinessType(data) {
    return client.post('/business-types/', data)
  },
  updateBusinessType(id, data) {
    return client.patch(`/business-types/${id}/`, data)
  },
  deleteBusinessType(id) {
    return client.delete(`/business-types/${id}/`)
  },
}
