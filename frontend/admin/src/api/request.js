import axios from 'axios'
import { apiBaseURL } from '@/utils/backend'
import router from '@/router'
import { useAuthStore } from '@/stores/auth'
import { flushEditors, isCurrentUnauthorized } from '@/utils/editorProtection.mjs'
import { installSessionInterceptors } from '@/utils/sessionRequests.mjs'
import { session } from './session'

const request = axios.create({ baseURL: apiBaseURL, timeout: 10000 })
let loginRedirect = null

async function expire(error) {
  const config = error.config || {}
  if (!isCurrentUnauthorized(config._authToken, session.getToken(), config.url)) return
  const returnTo = router.currentRoute.value.fullPath
  const saved = flushEditors()
  useAuthStore().clearSession(config._authToken)
  if (saved && !config.skipAuthRedirect && router.currentRoute.value.path !== '/login' && !loginRedirect) {
    loginRedirect = router.replace({ path: '/login', query: { redirect: returnTo, expired: '1' } })
    try { await loginRedirect } finally { loginRedirect = null }
  }
}

installSessionInterceptors(request, { session, expire })

export default request
