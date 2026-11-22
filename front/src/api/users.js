import client from './client'

export const usersApi = {
  getUsers(params = {}) {
    return client.get('/users/', { params })
  },
  getUser(id) {
    return client.get(`/users/${id}/`)
  },
  approveUser(id, data = {}) {
    return client.post(`/users/${id}/approve/`, data)
  },
  rejectUser(id) {
    return client.post(`/users/${id}/reject/`)
  },
  updateUser(id, data) {
    return client.patch(`/users/${id}/`, data)
  },
  deleteUser(id) {
    return client.delete(`/users/${id}/`)
  },
}
