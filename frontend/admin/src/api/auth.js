import request from './request'

export function login(username, password) {
  return request.post('/admin/auth/login', { username, password })
}

export function getMe() {
  return request.get('/admin/auth/me')
}

export function uploadAvatar(file) {
  const form = new FormData()
  form.append('file', file)
  return request.post('/admin/auth/avatar', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function deleteAvatar() {
  return request.delete('/admin/auth/avatar')
}
