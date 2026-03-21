import request from './request'

export const getScopes = () => request.get('/admin/access-keys/scopes')
export const getAccessKeys = () => request.get('/admin/access-keys')
export const createAccessKey = (data) => request.post('/admin/access-keys', data)
export const updateAccessKey = (id, data) => request.put(`/admin/access-keys/${id}`, data)
export const deleteAccessKey = (id) => request.delete(`/admin/access-keys/${id}`)
