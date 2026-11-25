import client from './client'

export const webkassaApi = {
  getRegisters(params = {}) {
    return client.get('/webkassa/registers/', { params })
  },
  getRegister(id) {
    return client.get(`/webkassa/registers/${id}/`)
  },
  updateRegister(id, data) {
    return client.patch(`/webkassa/registers/${id}/`, data)
  },
  deleteRegister(id) {
    return client.delete(`/webkassa/registers/${id}/`)
  },
  uploadCsv(formData) {
    return client.post('/webkassa/registers/upload-csv/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  getDashboard(params = {}) {
    return client.get('/webkassa/registers/dashboard/', { params })
  },
  getCtoList() {
    return client.get('/webkassa/registers/cto-list/')
  },
  getOfdList() {
    return client.get('/webkassa/registers/ofd-list/')
  },
}
