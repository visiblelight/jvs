import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

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

router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.guest) {
    token ? next('/home') : next()
    return
  }
  if (!token) {
    next('/login')
    return
  }
  const authStore = useAuthStore()
  if (!authStore.user) {
    try { await authStore.fetchUser() } catch { next('/login'); return }
  }
  if (to.meta.module && !authStore.canAccess(to.meta.module)) {
    next('/home')
    return
  }
  next()
})

export default router
