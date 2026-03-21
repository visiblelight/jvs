import request from './request'

// 分类
export const getCategories = () => request.get('/admin/news/categories')
export const createCategory = (data) => request.post('/admin/news/categories', data)
export const updateCategory = (id, data) => request.put(`/admin/news/categories/${id}`, data)
export const deleteCategory = (id) => request.delete(`/admin/news/categories/${id}`)

// 来源
export const getSources = () => request.get('/admin/news/sources')
export const createSource = (data) => request.post('/admin/news/sources', data)
export const updateSource = (id, data) => request.put(`/admin/news/sources/${id}`, data)
export const deleteSource = (id) => request.delete(`/admin/news/sources/${id}`)

// 文章
export const getArticles = (params) => request.get('/admin/news/articles', { params })
export const getArticle = (id) => request.get(`/admin/news/articles/${id}`)
export const createArticle = (data) => request.post('/admin/news/articles', data)
export const updateArticle = (id, data) => request.put(`/admin/news/articles/${id}`, data)
export const deleteArticle = (id) => request.delete(`/admin/news/articles/${id}`)
