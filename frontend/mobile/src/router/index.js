import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/home',
  },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
