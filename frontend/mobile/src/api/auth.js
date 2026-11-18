import request from './request'
import { session } from './session'

export const login = (username, password) =>
  session.login(username, password)

export const getMe = (config) =>
  request.get('/admin/auth/me', config)

export const changePassword = (data) =>
  request.put('/admin/auth/password', data)
