import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { login as loginApi, getMe } from '@/api/auth'
import router from '@/router'

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
    await fetchUser()
  }

  async function fetchUser() {
    const { data } = await getMe()
    user.value = data
    avatarVersion.value = Date.now()
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    router.push('/login')
  }

  return { token, user, avatarVersion, isSuperuser, modules, canAccess, login, fetchUser, logout }
})
