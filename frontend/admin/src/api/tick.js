import request from './request'

export const getTasks = (params) => request.get('/admin/tick/tasks', { params })
export const getTask = (id) => request.get(`/admin/tick/tasks/${id}`)
export const createTask = (data) => request.post('/admin/tick/tasks', data)
export const updateTask = (id, data) => request.put(`/admin/tick/tasks/${id}`, data)
export const deleteTask = (id) => request.delete(`/admin/tick/tasks/${id}`)
export const doTick = (id, data = {}) => request.post(`/admin/tick/tasks/${id}/tick`, data)
export const undoTick = (id) => request.delete(`/admin/tick/tasks/${id}/tick`)
export const getLogs = (id, params) => request.get(`/admin/tick/tasks/${id}/logs`, { params })
export const getAllLogs = (params) => request.get('/admin/tick/logs', { params })
export const deleteLog = (id) => request.delete(`/admin/tick/logs/${id}`)
export const makeupTick = (id, data) => request.post(`/admin/tick/tasks/${id}/makeup`, data)
