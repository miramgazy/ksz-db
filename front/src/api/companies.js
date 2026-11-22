import client from './client'

export const companiesApi = {
  getCompanies(params = {}) {
    return client.get('/companies/', { params })
  },
  getCompany(id) {
    return client.get(`/companies/${id}/`)
  },
  createCompany(data) {
    return client.post('/companies/', data)
  },
  updateCompany(id, data) {
    return client.patch(`/companies/${id}/`, data)
  },
  deleteCompany(id) {
    return client.delete(`/companies/${id}/`)
  },
  getFilterOptions() {
    return client.get('/companies/filter_options/')
  },
  getChains() {
    return client.get('/companies/chains/')
  },
  getClearbatParams(id) {
    return client.get(`/companies/${id}/clearbat_params/`)
  },
}
