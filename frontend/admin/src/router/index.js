import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
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

router.beforeEach(async (to) => {
  if (!flushEditors()) return false
  const token = localStorage.getItem('token')
  if (to.meta.guest) return token ? '/dashboard' : true
  const login = { path: '/login', query: { redirect: to.fullPath } }
  if (!token) return login
  const authStore = useAuthStore()
  if (authStore.token !== token) {
    authStore.token = token
    authStore.user = null
  }
  if (!authStore.user) {
    try { await authStore.fetchUser({ skipAuthRedirect: true }) }
    catch (error) {
      const target = authFailureRedirect(token, localStorage.getItem('token'), to.fullPath, error.response?.status)
      if (target) authStore.clearSession()
      return target
    }
  }
  if (to.meta.superuser && !authStore.isSuperuser) return '/dashboard'
  if (to.meta.module && !authStore.canAccess(to.meta.module)) return '/dashboard'
  return true
})

export default router
