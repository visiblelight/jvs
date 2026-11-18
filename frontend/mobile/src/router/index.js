import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { session } from '@/api/session'
import { terminalAuthError, sameSession, tokenClaims } from '@/utils/session.mjs'
import { flushEditors, authFailureRedirect } from '@/utils/editorProtection.mjs'

const routes = [
  { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue'), meta: { guest: true } },
  {
    path: '/',
    component: () => import('@/layouts/MobileLayout.vue'),
    children: [
      { path: '', redirect: '/home' },
      { path: 'home',    name: 'home',    component: () => import('@/views/HomeView.vue'),              meta: { tabBar: true } },
      { path: 'profile', name: 'profile', component: () => import('@/views/profile/ProfileView.vue'),   meta: { tabBar: true } },
      { path: 'todo',    name: 'todo',    component: () => import('@/views/todo/TodoView.vue'),         meta: { module: 'todo' } },
      { path: 'tick',    name: 'tick',    component: () => import('@/views/tick/TickView.vue'),         meta: { module: 'tick' } },
      { path: 'news',    name: 'news',    component: () => import('@/views/news/NewsView.vue'),         meta: { module: 'news' } },
      { path: 'news/:id', name: 'news-detail', component: () => import('@/views/news/NewsDetailView.vue'), meta: { module: 'news' } },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach(async to => {
  if (!flushEditors()) return false
  const original = session.getToken()
  let token
  try { token = await session.ensureAccess({ expectedToken: original }) }
  catch (error) {
    if (error.code === 'SESSION_CHANGED') return false
    // Temporary renewal failures can keep an already loaded identity on screen.
    // API calls still require successful renewal before sending this expired JWT.
    const auth = useAuthStore()
    if (!terminalAuthError(error) && original === session.getToken() && Number(tokenClaims(original).sub) === auth.user?.id) {
      token = original
    } else {
      if (terminalAuthError(error)) auth.clearSession(original)
      if (to.meta.guest) return true
      return { path: '/login', query: { redirect: to.fullPath, ...(terminalAuthError(error) ? { expired: '1' } : { retry: '1' }) } }
    }
  }
  if (to.meta.guest) return token && !to.query.retry ? '/home' : true
  const login = { path: '/login', query: { redirect: to.fullPath } }
  if (!token) return login
  const authStore = useAuthStore()
  if (authStore.token !== token) {
    if (!sameSession(authStore.token, token)) authStore.user = null
    authStore.token = token
  }
  if (!authStore.user) {
    try { await authStore.fetchUser({ skipAuthRedirect: true }) }
    catch (error) {
      const current = session.getToken()
      const target = authFailureRedirect(token, sameSession(token, current) ? token : current, to.fullPath, error.response?.status)
      if (target && terminalAuthError(error)) authStore.clearSession(current)
      return target
    }
  }
  if (to.meta.superuser && !authStore.isSuperuser) return '/home'
  if (to.meta.module && !authStore.canAccess(to.meta.module)) return '/home'
  return true
})

export default router
