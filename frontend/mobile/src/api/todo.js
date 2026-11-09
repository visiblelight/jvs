import request from './request'

export const getCategories = () => request.get('/admin/todo/categories')
export const getTags = () => request.get('/admin/todo/tags')
export const getItems = (params) => request.get('/admin/todo/items', { params })
export const getItem = (id, config) => request.get(`/admin/todo/items/${id}`, config)
export const createItem = (data, config) => request.post('/admin/todo/items', data, config)
export const updateItem = (id, data, config) => request.put(`/admin/todo/items/${id}`, data, config)
export const deleteItem = (id) => request.delete(`/admin/todo/items/${id}`)
