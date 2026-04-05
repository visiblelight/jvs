import request from './request'

export function listUsers() {
  return request.get('/admin/users')
}

export function getUser(id) {
  return request.get(`/admin/users/${id}`)
}

export function createUser(payload) {
  return request.post('/admin/users', payload)
}

export function updateUser(id, payload) {
  return request.put(`/admin/users/${id}`, payload)
}

export function setUserModules(id, modules) {
  return request.put(`/admin/users/${id}/modules`, { modules })
}

export function listModules() {
  return request.get('/admin/modules')
}
