<template>
  <div class="admin-layout">
    <!-- Icon-only sidebar -->
    <aside class="sidebar">
      <div class="sidebar-logo">
        <div class="logo-mark">
          <svg viewBox="0 0 24 24" fill="none" width="18" height="18">
            <path d="M3 3h8v8H3zM13 3h8v8h-8zM3 13h8v8H3zM17 13a4 4 0 100 8 4 4 0 000-8z" fill="currentColor" opacity="0.9"/>
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
}

/* ── Sidebar ── */
.sidebar {
  width: var(--sidebar-width);
  background: var(--color-surface-sidebar);
  border-right: 1px solid var(--color-border-light);
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 20;
  padding: 12px 0;
}

.sidebar-logo {
  margin-bottom: 20px;
  padding: 4px 0 12px;
  border-bottom: 1px solid var(--color-border-light);
  width: 100%;
  display: flex;
  justify-content: center;
}

.logo-mark {
  width: 36px;
  height: 36px;
  background: var(--color-accent);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  transition: transform var(--transition-fast);
}

.logo-mark:hover {
  transform: scale(1.05);
}

/* Nav */
.sidebar-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  width: 100%;
  padding: 0 10px;
}

.sidebar-bottom {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  width: 100%;
  padding: 0 10px;
  padding-top: 12px;
  border-top: 1px solid var(--color-border-light);
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
  height: 40px;
  border-radius: var(--radius-md);
  color: var(--color-text-sidebar);
  transition: all var(--transition-fast);
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
}

.nav-item--active {
  color: var(--color-accent-text);
  background: var(--color-accent-subtle);
}

.nav-item--active::before {
  content: '';
  position: absolute;
  left: -10px;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  background: var(--color-accent);
  border-radius: 0 2px 2px 0;
}

.nav-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

/* Tooltip */
.nav-tooltip {
  position: absolute;
  left: calc(100% + 10px);
  top: 50%;
  transform: translateY(-50%) translateX(-4px);
  background: var(--color-text);
  color: var(--color-text-inverse);
  font-family: var(--font-body);
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
  padding: 5px 10px;
  border-radius: var(--radius-sm);
  opacity: 0;
  pointer-events: none;
  transition: opacity var(--transition-fast), transform var(--transition-fast);
  z-index: 100;
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
  transform: translateY(-50%) translateX(0);
}

/* Avatar link */
.nav-avatar-link {
  border-radius: 50%;
  padding: 4px;
}

.nav-avatar-link.nav-item--active {
  background: var(--color-accent-subtle);
}

.nav-avatar-link.nav-item--active::before {
  display: none;
}

/* ── Main Area ── */
.main-area {
  flex: 1;
  margin-left: var(--sidebar-width);
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.content {
  flex: 1;
  background: var(--color-bg);
}

/* ── Page transitions ── */
.page-enter-active,
.page-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(6px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
