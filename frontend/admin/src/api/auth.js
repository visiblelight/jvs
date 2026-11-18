import request from './request'
import { session } from './session'

export function login(username, password) {
  return session.login(username, password)
}

export function getMe(config) {
  return request.get('/admin/auth/me', config)
}

export function uploadAvatar(file) {
  const form = new FormData()
  form.append('file', file)
  return request.post('/admin/auth/avatar', form)
}

export function deleteAvatar() {
  return request.delete('/admin/auth/avatar')
}
