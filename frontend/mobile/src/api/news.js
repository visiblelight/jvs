import request from './request'

export const getCategories = () => request.get('/admin/news/categories')
export const getArticles = (params) => request.get('/admin/news/articles', { params })
export const getArticle = (id) => request.get(`/admin/news/articles/${id}`)
