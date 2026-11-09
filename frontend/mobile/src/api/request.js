import axios from 'axios'
import { apiBaseURL } from '@/utils/backend'
import router from '@/router'
import { useAuthStore } from '@/stores/auth'
import { flushEditors, isCurrentUnauthorized, tokenUserId } from '@/utils/editorProtection.mjs'

const request = axios.create({ baseURL: apiBaseURL, timeout: 10000 })
let loginRedirect = null

request.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (config.expectedUserId && token && tokenUserId(token) !== config.expectedUserId) {
    throw new Error('账号已在其他窗口改变，草稿已保留。请重新登录原账号后继续。')
  }
  config._authToken = token
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

request.interceptors.response.use(response => response, async error => {
  if (error.response?.status === 401 && isCurrentUnauthorized(
    error.config?._authToken, localStorage.getItem('token'), error.config?.url,
  )) {
    // Capture and persist before clearing auth or allowing the editor to unmount.
    const returnTo = router.currentRoute.value.fullPath
    const saved = flushEditors()
    useAuthStore().clearSession()
    if (saved && !error.config?.skipAuthRedirect && router.currentRoute.value.path !== '/login' && !loginRedirect) {
      loginRedirect = router.replace({ path: '/login', query: { redirect: returnTo, expired: '1' } })
      try { await loginRedirect } finally { loginRedirect = null }
    }
  }
  return Promise.reject(error)
})

export default request
