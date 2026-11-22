import client from './client'

export const servicesApi = {
  // Service Types (Catalog)
  getServiceTypes(params = {}) {
    return client.get('/service-types/', { params })
  },
  createServiceType(data) {
    return client.post('/service-types/', data)
  },
  updateServiceType(id, data) {
    return client.patch(`/service-types/${id}/`, data)
  },
  deleteServiceType(id) {
    return client.delete(`/service-types/${id}/`)
  },

  // Company Services (Subscriptions)
  getCompanyServices(params = {}) {
    return client.get('/company-services/', { params })
  },
  getStats() {
    return client.get('/company-services/stats/')
  },
  createCompanyService(data) {
    return client.post('/company-services/', data)
  },
  updateCompanyService(id, data) {
    return client.patch(`/company-services/${id}/`, data)
  },
  deleteCompanyService(id) {
    return client.delete(`/company-services/${id}/`)
  },
  renewService(id, payload) {
    return client.post(`/company-services/${id}/renew/`, payload)
  },
}
