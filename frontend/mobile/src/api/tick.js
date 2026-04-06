import request from './request'

export const getTasks = (params) => request.get('/admin/tick/tasks', { params })
export const getTask = (id) => request.get(`/admin/tick/tasks/${id}`)
export const doTick = (id, data = {}) => request.post(`/admin/tick/tasks/${id}/tick`, data)
export const undoTick = (id) => request.delete(`/admin/tick/tasks/${id}/tick`)
