import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { login as loginApi, getMe } from '@/api/auth'
import router from '@/router'
import { session } from '@/api/session'
import { terminalAuthError, tokenClaims, sameSession } from '@/utils/session.mjs'
import { flushEditors } from '@/utils/editorProtection.mjs'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)
  const avatarVersion = ref(0)

  const isSuperuser = computed(() => !!user.value?.is_superuser)
  const modules = computed(() => user.value?.modules || [])

  function canAccess(moduleKey) {
    if (!user.value) return false
    if (user.value.is_superuser) return true
    return (user.value.modules || []).includes(moduleKey)
  }

  async function login(username, password) {
    const { data } = await loginApi(username, password)
    token.value = data.access_token
    try { await fetchUser() }
    catch (error) {
      if (terminalAuthError(error) && session.getToken() === data.access_token) clearSession()
      throw error
    }
  }

  async function fetchUser(config) {
    const requestedToken = localStorage.getItem('token')
    const { data } = await getMe(config)
    const current = session.getToken()
    if ((!sameSession(current, requestedToken) && current !== requestedToken) || Number(tokenClaims(current).sub) !== data.id) throw new Error('登录账号已改变，请刷新页面')
    token.value = current || ''
    user.value = data
    avatarVersion.value = Date.now()
  }

  function clearSession(expected = session.getToken()) {
    if (!session.invalidate(expected)) return false
    token.value = ''
    user.value = null
    return true
  }

  async function logout({ localOnly = false, reason } = {}) {
    if (!flushEditors()) return
    try {
      if (localOnly) clearSession()
      else { await session.logout(); token.value = ''; user.value = null }
      await router.push({ path: '/login', query: reason ? { reason } : {} })
    } catch {
      window.alert('退出登录未完成，请检查网络后重试。')
    }
  }

  return { token, user, avatarVersion, isSuperuser, modules, canAccess, login, fetchUser, logout, clearSession }
})
