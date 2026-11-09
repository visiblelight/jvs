import request from './request'

export const login = (username, password) =>
  request.post('/admin/auth/login', { username, password })

export const getMe = (config) =>
  request.get('/admin/auth/me', config)

export const changePassword = (data) =>
  request.put('/admin/auth/password', data)
