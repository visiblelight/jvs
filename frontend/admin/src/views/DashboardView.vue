<template>
  <div class="dashboard">
    <div class="dash-inner">
      <!-- Hero greeting -->
      <header class="dash-hero">
        <div class="time-chip">{{ formattedTime }}</div>
        <h1 class="greeting">{{ greeting }}</h1>
        <p class="date-line">{{ formattedDate }}</p>
      </header>

      <!-- Stat strip -->
      <div class="stat-strip">
        <div class="stat-card stat-card--accent">
          <div class="stat-icon">
            <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16"><path d="M9 4.804A7.968 7.968 0 005.5 4c-1.255 0-2.443.29-3.5.804v10A7.969 7.969 0 015.5 14c1.396 0 2.696.397 3.8 1.08A7.968 7.968 0 0114.5 14c1.255 0 2.443.29 3.5.804v-10A7.968 7.968 0 0014.5 4c-1.255 0-2.443.29-3.5.804V12a1 1 0 11-2 0V4.804z"/></svg>
          </div>
          <div class="stat-content">
            <span class="stat-label">系统</span>
            <span class="stat-value">运行中</span>
          </div>
          <div class="stat-dot stat-dot--pulse"></div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">
            <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16"><path d="M2 10a8 8 0 1116 0 8 8 0 01-16 0zm8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 10a3.001 3.001 0 01-2 2.83V13a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z"/></svg>
          </div>
          <div class="stat-content">
            <span class="stat-label">账号</span>
            <span class="stat-value">{{ authStore.user?.username }}</span>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">
            <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16"><path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd"/></svg>
          </div>
          <div class="stat-content">
            <span class="stat-label">今天</span>
            <span class="stat-value">{{ shortDate }}</span>
          </div>
        </div>
      </div>

      <!-- Module cards -->
      <div class="module-grid">
        <router-link to="/todo" class="module-card">
          <div class="module-icon-wrap">
            <svg viewBox="0 0 24 24" fill="none" width="22" height="22">
              <rect x="3" y="5" width="18" height="16" rx="2" stroke="currentColor" stroke-width="1.5"/>
              <path d="M7 9l2 2 4-4M7 15l2 2 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="module-text">
            <h3>ToDo</h3>
            <p>任务管理</p>
          </div>
          <div class="module-arrow">
            <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14"><path d="M6.22 3.22a.75.75 0 011.06 0l4.25 4.25a.75.75 0 010 1.06l-4.25 4.25a.75.75 0 01-1.06-1.06L9.94 8 6.22 4.28a.75.75 0 010-1.06z"/></svg>
          </div>
        </router-link>

        <router-link to="/news" class="module-card">
          <div class="module-icon-wrap">
            <svg viewBox="0 0 24 24" fill="none" width="22" height="22">
              <rect x="3" y="4" width="18" height="16" rx="2" stroke="currentColor" stroke-width="1.5"/>
              <path d="M7 8h10M7 12h7M7 16h5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="module-text">
            <h3>新闻</h3>
            <p>文章管理</p>
          </div>
          <div class="module-arrow">
            <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14"><path d="M6.22 3.22a.75.75 0 011.06 0l4.25 4.25a.75.75 0 010 1.06l-4.25 4.25a.75.75 0 01-1.06-1.06L9.94 8 6.22 4.28a.75.75 0 010-1.06z"/></svg>
          </div>
        </router-link>

        <router-link to="/profile" class="module-card">
          <div class="module-icon-wrap">
            <svg viewBox="0 0 24 24" fill="none" width="22" height="22">
              <circle cx="12" cy="8" r="4" stroke="currentColor" stroke-width="1.5"/>
              <path d="M4 20c0-4 3.582-7 8-7s8 3 8 7" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="module-text">
            <h3>个人中心</h3>
            <p>账号与密钥</p>
          </div>
          <div class="module-arrow">
            <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14"><path d="M6.22 3.22a.75.75 0 011.06 0l4.25 4.25a.75.75 0 010 1.06l-4.25 4.25a.75.75 0 01-1.06-1.06L9.94 8 6.22 4.28a.75.75 0 010-1.06z"/></svg>
          </div>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 6) return '夜深了'
  if (h < 12) return '早上好'
  if (h < 18) return '下午好'
  return '晚上好'
})

const formattedDate = computed(() =>
  new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' })
)

const shortDate = computed(() =>
  new Date().toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
)

const formattedTime = computed(() =>
  new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', hour12: false })
)
</script>

<style scoped>
.dashboard {
  min-height: calc(100vh - 0px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 32px;
  background: var(--color-bg);
}

.dash-inner {
  width: 100%;
  max-width: 640px;
  animation: fadeUp 0.4s cubic-bezier(0.22, 1, 0.36, 1) both;
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Hero */
.dash-hero {
  margin-bottom: 40px;
}

.time-chip {
  display: inline-flex;
  align-items: center;
  font-family: var(--font-heading);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--color-accent-text);
  background: var(--color-accent-subtle);
  padding: 4px 12px;
  border-radius: 100px;
  margin-bottom: 16px;
}

.greeting {
  font-family: var(--font-heading);
  font-size: 52px;
  font-weight: 800;
  color: var(--color-text);
  letter-spacing: -2px;
  line-height: 1;
  margin-bottom: 10px;
}

.date-line {
  font-size: 14px;
  color: var(--color-text-tertiary);
  font-weight: 400;
}

/* Stat strip */
.stat-strip {
  display: flex;
  gap: 10px;
  margin-bottom: 28px;
  flex-wrap: wrap;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: var(--color-surface);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  flex: 1;
  min-width: 140px;
  position: relative;
  transition: all var(--transition-fast);
}

.stat-card:hover {
  border-color: var(--color-border);
  transform: translateY(-1px);
}

.stat-card--accent {
  border-color: var(--color-accent-subtle);
  background: var(--color-accent-subtle);
}

.stat-icon {
  color: var(--color-accent-text);
  display: flex;
  flex-shrink: 0;
}

.stat-content {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.stat-label {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.8px;
  text-transform: uppercase;
  color: var(--color-text-tertiary);
}

.stat-value {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text);
}

.stat-dot {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 7px;
  height: 7px;
  background: var(--color-success);
  border-radius: 50%;
}

.stat-dot--pulse {
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(5, 150, 105, 0.4); }
  50% { box-shadow: 0 0 0 6px rgba(5, 150, 105, 0); }
}

/* Module grid */
.module-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.module-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 18px;
  background: var(--color-surface);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  transition: all var(--transition-fast);
  cursor: pointer;
  animation: cardIn 0.4s cubic-bezier(0.22, 1, 0.36, 1) both;
}

.module-card:nth-child(1) { animation-delay: 0.08s; }
.module-card:nth-child(2) { animation-delay: 0.14s; }
.module-card:nth-child(3) { animation-delay: 0.20s; }

@keyframes cardIn {
  from { opacity: 0; transform: translateX(-12px); }
  to { opacity: 1; transform: translateX(0); }
}

.module-card:hover {
  border-color: var(--color-accent);
  transform: translateX(4px);
  box-shadow: var(--shadow-sm);
}

.module-icon-wrap {
  width: 44px;
  height: 44px;
  background: var(--color-accent-subtle);
  color: var(--color-accent-text);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: background var(--transition-fast);
}

.module-card:hover .module-icon-wrap {
  background: var(--color-accent);
  color: white;
}

.module-text {
  flex: 1;
}

.module-text h3 {
  font-family: var(--font-heading);
  font-size: 15px;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 1px;
  letter-spacing: -0.3px;
}

.module-text p {
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.module-arrow {
  color: var(--color-text-tertiary);
  transition: all var(--transition-fast);
}

.module-card:hover .module-arrow {
  color: var(--color-accent-text);
  transform: translateX(2px);
}
</style>
