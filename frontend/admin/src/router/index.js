import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import LoginView from '@/views/LoginView.vue'
import AdminLayout from '@/layouts/AdminLayout.vue'
import DashboardView from '@/views/DashboardView.vue'
import TodoView from '@/views/todo/TodoView.vue'
import NewsView from '@/views/news/NewsView.vue'
import ProfileView from '@/views/profile/ProfileView.vue'
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

router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('token')

  if (to.meta.guest) {
    if (token) {
      next('/dashboard')
    } else {
      next()
    }
    return
  }

  if (!token) {
    next('/login')
    return
  }

  const authStore = useAuthStore()
  if (!authStore.user) {
    try {
      await authStore.fetchUser()
    } catch {
      next('/login')
      return
    }
  }

  if (to.meta.superuser && !authStore.isSuperuser) {
    next('/dashboard')
    return
  }

  if (to.meta.module && !authStore.canAccess(to.meta.module)) {
    next('/dashboard')
    return
  }

  next()
})

export default router
