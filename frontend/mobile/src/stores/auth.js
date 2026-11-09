import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { login as loginApi, getMe } from '@/api/auth'
import router from '@/router'
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
    localStorage.setItem('token', data.access_token)
    try { await fetchUser() }
    catch (error) {
      if (localStorage.getItem('token') === data.access_token) clearSession()
      throw error
    }
  }

  async function fetchUser(config) {
    const requestedToken = localStorage.getItem('token')
    const { data } = await getMe(config)
    if (localStorage.getItem('token') !== requestedToken) throw new Error('登录账号已改变，请刷新页面')
    user.value = data
    avatarVersion.value = Date.now()
  }

  function clearSession() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
  }

  function logout() {
    if (!flushEditors()) return
    clearSession()
    router.push('/login')
  }

  return { token, user, avatarVersion, isSuperuser, modules, canAccess, login, fetchUser, logout, clearSession }
})
