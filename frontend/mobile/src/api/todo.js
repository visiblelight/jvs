import request from './request'

export const getCategories = () => request.get('/admin/todo/categories')
export const getTags = () => request.get('/admin/todo/tags')
export const getItems = (params) => request.get('/admin/todo/items', { params })
export const getItem = (id) => request.get(`/admin/todo/items/${id}`)
export const createItem = (data) => request.post('/admin/todo/items', data)
export const updateItem = (id, data) => request.put(`/admin/todo/items/${id}`, data)
export const deleteItem = (id) => request.delete(`/admin/todo/items/${id}`)
