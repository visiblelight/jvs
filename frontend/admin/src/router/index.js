import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { session } from '@/api/session'
import { terminalAuthError, sameSession, tokenClaims } from '@/utils/session.mjs'
import { flushEditors, authFailureRedirect } from '@/utils/editorProtection.mjs'
import LoginView from '@/views/LoginView.vue'
import AdminLayout from '@/layouts/AdminLayout.vue'
import DashboardView from '@/views/DashboardView.vue'
import TodoView from '@/views/todo/TodoView.vue'
import NewsView from '@/views/news/NewsView.vue'
import ProfileView from '@/views/profile/ProfileView.vue'
import TickView from '@/views/tick/TickView.vue'
import UsersView from '@/views/users/UsersView.vue'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { guest: true },
  },
  {
    path: '/',
    component: AdminLayout,
    children: [
      {
        path: '',
        redirect: '/dashboard',
      },
      {
        path: 'dashboard',
        name: 'dashboard',
        component: DashboardView,
      },
      {
        path: 'todo',
        name: 'todo',
        component: TodoView,
        meta: { module: 'todo' },
      },
      {
        path: 'tick',
        name: 'tick',
        component: TickView,
        meta: { module: 'tick' },
      },
      {
        path: 'news',
        name: 'news',
        component: NewsView,
        meta: { module: 'news' },
      },
      {
        path: 'profile',
        name: 'profile',
        component: ProfileView,
      },
      {
        path: 'users',
        name: 'users',
        component: UsersView,
        meta: { superuser: true },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
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
  if (to.meta.guest) return token && !to.query.retry ? '/dashboard' : true
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
  if (to.meta.superuser && !authStore.isSuperuser) return '/dashboard'
  if (to.meta.module && !authStore.canAccess(to.meta.module)) return '/dashboard'
  return true
})

export default router
