import client from './client'

export const anydeskApi = {
  getAnydeskStations(params = {}) {
    return client.get('/anydesk/', { params })
  },
  createAnydeskStation(data) {
    return client.post('/anydesk/', data)
  },
  updateAnydeskStation(id, data) {
    return client.patch(`/anydesk/${id}/`, data)
  },
  deleteAnydeskStation(id) {
    return client.delete(`/anydesk/${id}/`)
  },
}
