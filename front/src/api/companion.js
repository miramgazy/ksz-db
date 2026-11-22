import client from './client'

export const companionApi = {
  async getStatus() {
    try {
      const res = await client.get('/companion/status/')
      return { online: res.data.online, data: res.data.data, user: res.data.user }
    } catch (e) {
      return { online: false, error: e.message }
    }
  },
  launchBackoffice(params) {
    return client.post('/companion/launch-backoffice/', params)
  },
  launchLicense(params) {
    return client.post('/companion/launch-license/', params)
  },
  insertClearbat(params) {
    return client.post('/companion/insert-clearbat/', params)
  },
  launchAnydesk(params) {
    return client.post('/companion/launch-anydesk/', params)
  },
}
