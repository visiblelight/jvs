<template>
  <nav class="bottom-nav">
    <router-link to="/home" class="nav-item" active-class="nav-item--active">
      <svg viewBox="0 0 24 24" fill="none" width="22" height="22">
        <path d="M3 9.5L12 3l9 6.5V20a1 1 0 01-1 1H5a1 1 0 01-1-1V9.5z"
          stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
        <path d="M9 21V12h6v9" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
      </svg>
      <span>首页</span>
    </router-link>
    <router-link to="/profile" class="nav-item" active-class="nav-item--active">
      <svg viewBox="0 0 24 24" fill="none" width="22" height="22">
        <circle cx="12" cy="8" r="4" stroke="currentColor" stroke-width="1.8"/>
        <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"
          stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
      </svg>
      <span>我的</span>
    </router-link>
  </nav>
</template>

<style scoped>
.bottom-nav {
  display: flex;
  background: var(--color-tab-bg);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  /* Floating Pill shape */
  margin: 0 16px calc(16px + var(--safe-bottom));
  border-radius: var(--radius-full);
  box-shadow: var(--shadow-floating);
  flex-shrink: 0;
  pointer-events: auto; /* Since wrapper is none */
  overflow: hidden;
}
.nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px 0 10px;
  color: var(--color-text-tertiary);
  transition: all var(--transition-fast);
  font-size: 11px;
  font-weight: 500;
}
.nav-item:active {
  transform: scale(0.92);
}
.nav-item--active {
  color: var(--color-accent);
}
</style>
