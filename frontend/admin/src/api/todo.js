import request from './request'

// 分类
export const getCategories = () => request.get('/admin/todo/categories')
export const createCategory = (data) => request.post('/admin/todo/categories', data)
export const updateCategory = (id, data) => request.put(`/admin/todo/categories/${id}`, data)
export const deleteCategory = (id) => request.delete(`/admin/todo/categories/${id}`)

// 标签
export const getTags = () => request.get('/admin/todo/tags')
export const createTag = (data) => request.post('/admin/todo/tags', data)
export const updateTag = (id, data) => request.put(`/admin/todo/tags/${id}`, data)
export const deleteTag = (id) => request.delete(`/admin/todo/tags/${id}`)

// 事项
export const getItems = (params) => request.get('/admin/todo/items', { params })
export const getItem = (id) => request.get(`/admin/todo/items/${id}`)
export const createItem = (data) => request.post('/admin/todo/items', data)
export const updateItem = (id, data) => request.put(`/admin/todo/items/${id}`, data)
export const deleteItem = (id) => request.delete(`/admin/todo/items/${id}`)
export const updateItemStatus = (id, status) => request.patch(`/admin/todo/items/${id}/status`, { status })
