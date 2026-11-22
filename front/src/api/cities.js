import client from './client'

export const citiesApi = {
  getCities(params = {}) {
    return client.get('/cities/', { params })
  },
  createCity(name) {
    return client.post('/cities/', { name })
  },
  updateCity(id, name) {
    return client.patch(`/cities/${id}/`, { name })
  },
  deleteCity(id) {
    return client.delete(`/cities/${id}/`)
  },
}
