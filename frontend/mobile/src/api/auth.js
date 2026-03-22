import request from './request'

export const login = (username, password) =>
  request.post('/admin/auth/login', { username, password })

export const getMe = () =>
  request.get('/admin/auth/me')

export const changePassword = (data) =>
  request.put('/admin/auth/password', data)
