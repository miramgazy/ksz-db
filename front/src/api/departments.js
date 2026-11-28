import client from './client'

export const departmentsApi = {
  getDepartments(params = {}) {
    return client.get('/departments/', { params })
  },
  createDepartment(data) {
    return client.post('/departments/', data)
  },
  updateDepartment(id, data) {
    return client.patch(`/departments/${id}/`, data)
  },
  deleteDepartment(id) {
    return client.delete(`/departments/${id}/`)
  },
}
