<template>
  <div class="admin-layout">
    <!-- Icon-only sidebar -->
    <aside class="sidebar">
      <div class="sidebar-logo">
        <div class="logo-mark">
          <svg viewBox="0 0 32 32" width="28" height="28">
            <defs>
              <linearGradient id="jvs-g" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#818CF8"/>
                <stop offset="100%" stop-color="#4F46E5"/>
              </linearGradient>
            </defs>
            <rect width="32" height="32" rx="7" fill="url(#jvs-g)"/>
            <path d="M20 7 L20 22 C20 28 10 28 10 21"
                  fill="none" stroke="white" stroke-width="5.5"
                  stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
      </div>

      <nav class="sidebar-nav">
        <div
          v-for="item in menuItems"
          :key="item.path"
          class="nav-item-wrap"
        >
          <router-link
            :to="item.path"
            class="nav-item"
            active-class="nav-item--active"
          >
            <svg class="nav-icon" viewBox="0 0 20 20" fill="currentColor" v-html="item.svg"></svg>
          </router-link>
          <div class="nav-tooltip">{{ item.label }}</div>
        </div>
      </nav>

      <div class="sidebar-bottom">
        <!-- Theme toggle -->
        <div class="nav-item-wrap">
          <button class="nav-item nav-item--btn" @click="themeStore.toggle()" :title="themeStore.theme === 'light' ? '夜间模式' : '日间模式'">
            <svg v-if="themeStore.theme === 'light'" viewBox="0 0 20 20" fill="currentColor" width="18" height="18"><path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"/></svg>
            <svg v-else viewBox="0 0 20 20" fill="currentColor" width="18" height="18"><path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clip-rule="evenodd"/></svg>
          </button>
          <div class="nav-tooltip">{{ themeStore.theme === 'light' ? '夜间模式' : '日间模式' }}</div>
        </div>

        <!-- Profile / logout -->
        <div class="nav-item-wrap">
          <router-link
            to="/profile"
            class="nav-item nav-avatar-link"
            active-class="nav-item--active"
          >
            <UserAvatar :avatar="authStore.user?.avatar" :size="32" :ts="authStore.avatarVersion" />
          </router-link>
          <div class="nav-tooltip">{{ authStore.user?.username }}</div>
        </div>
      </div>
    </aside>

    <!-- Main content -->
    <div class="main-area">
      <main class="content">
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import UserAvatar from '@/components/UserAvatar.vue'

const route = useRoute()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const menuItems = [
  {
    path: '/dashboard',
    label: '首页',
    svg: '<path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"/>',
  },
  {
    path: '/todo',
    label: 'ToDo',
    svg: '<path d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 011 1v3.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-1.5-1.5a1 1 0 111.414-1.414l.793.793V8a1 1 0 011-1z"/>',
  },
  {
    path: '/news',
    label: '新闻',
    svg: '<path d="M2 3a1 1 0 011-1h11a1 1 0 011 1v2.586l1.707-1.293A1 1 0 0118 5.414V14.586a1 1 0 01-1.707.707L14 13.586V16a1 1 0 01-1 1H3a1 1 0 01-1-1V3zm12 10V5H4v10h10zM6 7h6v2H6V7zm0 3h4v2H6v-2z"/>',
  },
]
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
  display: flex;
  background: transparent;
}

/* ── Sidebar Island ── */
.sidebar {
  width: var(--sidebar-width);
  background: var(--color-surface-sidebar);
  border: 1px solid var(--color-border);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md);
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
  position: fixed;
  top: 16px;
  left: 16px;
  bottom: 16px;
  z-index: 20;
  padding: 16px 0;
}

.sidebar-logo {
  margin-bottom: 24px;
  width: 100%;
  display: flex;
  justify-content: center;
}

.logo-mark {
  width: 36px;
  height: 36px;
  background: transparent;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  transition: transform var(--transition-base);
}

.logo-mark:hover {
  transform: scale(1.05);
  filter: brightness(1.1);
}

/* Nav */
.sidebar-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 0 12px;
}

.sidebar-bottom {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 0 12px;
  padding-top: 16px;
  border-top: 1px solid var(--color-border);
}

.nav-item-wrap {
  position: relative;
  width: 100%;
}

.nav-item {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 44px;
  border-radius: var(--radius-md);
  color: var(--color-text-sidebar);
  transition: all var(--transition-base);
  position: relative;
}

.nav-item--btn {
  border: none;
  background: none;
  cursor: pointer;
  font-size: inherit;
}

.nav-item:hover {
  color: var(--color-text-sidebar-active);
  background: var(--color-surface-hover);
  transform: scale(0.96);
}

.nav-item--active {
  color: var(--color-accent-text);
  background: var(--color-accent-subtle);
  transform: scale(1);
}

.nav-item--active:hover {
  transform: scale(0.96);
}

.nav-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

/* Tooltip */
.nav-tooltip {
  position: absolute;
  left: calc(100% + 14px);
  top: 50%;
  transform: translateY(-50%) translateX(-4px) scale(0.95);
  background: var(--color-text);
  color: var(--color-text-inverse);
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
  padding: 6px 12px;
  border-radius: var(--radius-sm);
  opacity: 0;
  pointer-events: none;
  transition: all var(--transition-fast);
  z-index: 100;
  box-shadow: var(--shadow-sm);
}

.nav-tooltip::before {
  content: '';
  position: absolute;
  right: 100%;
  top: 50%;
  transform: translateY(-50%);
  border: 5px solid transparent;
  border-right-color: var(--color-text);
}

.nav-item-wrap:hover .nav-tooltip {
  opacity: 1;
  transform: translateY(-50%) translateX(0) scale(1);
}

/* Avatar link */
.nav-avatar-link {
  border-radius: 50%;
  padding: 4px;
}

.nav-avatar-link:hover {
  transform: scale(1.05);
}

.nav-avatar-link.nav-item--active {
  background: var(--color-accent-subtle);
}

/* ── Main Area ── */
.main-area {
  flex: 1;
  /* Accommodate the left floating sidebar (68px width + 16px left + 16px space) */
  margin-left: calc(var(--sidebar-width) + 32px);
  margin-top: 16px;
  margin-right: 16px;
  margin-bottom: 16px;
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - 32px);
  background: var(--color-surface);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-radius: var(--radius-xl);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.content {
  flex: 1;
  background: transparent;
  position: relative;
}

/* ── Page transitions ── */
.page-enter-active,
.page-leave-active {
  transition: opacity 0.25s cubic-bezier(0.4, 0, 0.2, 1), transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.page-enter-from {
  opacity: 0;
  transform: translateY(8px) scale(0.99);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-8px) scale(0.99);
}
</style>
