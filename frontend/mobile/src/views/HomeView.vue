<template>
  <div class="home-page">
    <header class="home-header">
      <div class="greeting-block">
        <p class="greeting-sub">{{ greeting }}</p>
        <h1 class="greeting-name">{{ authStore.user?.username }}</h1>
      </div>
      <router-link to="/profile">
        <UserAvatar
          :avatar="authStore.user?.avatar"
          :size="40"
          :ts="authStore.avatarVersion"
        />
      </router-link>
    </header>

    <div v-if="showTodoStat || showNewsStat" class="stats-strip">
      <div v-if="showTodoStat" class="stat-item">
        <span class="stat-value">{{ todoStore.total }}</span>
        <span class="stat-label">待办事项</span>
      </div>
      <div v-if="showTodoStat && showNewsStat" class="stat-divider" />
      <div v-if="showNewsStat" class="stat-item">
        <span class="stat-value">{{ newsStore.total }}</span>
        <span class="stat-label">新闻文章</span>
      </div>
    </div>

    <div class="section-label">工作台</div>

    <div v-if="visibleModules.length === 0" class="no-modules">
      暂无可用板块，请联系管理员开通权限
    </div>
    <div v-else class="modules-grid">
      <button
        v-for="mod in visibleModules"
        :key="mod.path"
        class="module-card"
        @click="$router.push(mod.path)"
      >
        <div class="module-icon" :style="{ background: mod.bg }">
          <svg viewBox="0 0 24 24" fill="none" width="26" height="26" v-html="mod.svg" />
        </div>
        <span class="module-name">{{ mod.name }}</span>
        <span class="module-desc">{{ mod.desc }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useTodoStore } from '@/stores/todo'
import { useNewsStore } from '@/stores/news'
import UserAvatar from '@/components/UserAvatar.vue'

const authStore = useAuthStore()
const todoStore = useTodoStore()
const newsStore = useNewsStore()

const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 6)  return '深夜好'
  if (h < 12) return '早上好'
  if (h < 14) return '中午好'
  if (h < 18) return '下午好'
  return '晚上好'
})

const modules = [
  {
    name: '待办',
    desc: 'Todo 任务管理',
    path: '/todo',
    moduleKey: 'todo',
    bg: 'linear-gradient(135deg, #4F46E5, #7C3AED)',
    svg: '<path d="M9 11l3 3L22 4" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
  },
  {
    name: '新闻',
    desc: '文章资讯阅读',
    path: '/news',
    moduleKey: 'news',
    bg: 'linear-gradient(135deg, #0EA5E9, #0284C7)',
    svg: '<path d="M4 6h16M4 10h16M4 14h10M4 18h7" stroke="white" stroke-width="2" stroke-linecap="round"/>',
  },
]

const visibleModules = computed(() =>
  modules.filter((m) => authStore.canAccess(m.moduleKey))
)

const showTodoStat = computed(() => authStore.canAccess('todo'))
const showNewsStat = computed(() => authStore.canAccess('news'))

onMounted(() => {
  if (authStore.canAccess('todo')) todoStore.fetchItems()
  if (authStore.canAccess('news')) newsStore.fetchArticles(true)
})
</script>

<style scoped>
.home-page {
  height: 100%;
  overflow-y: auto;
  background: var(--color-bg);
  padding-top: var(--safe-top);
}

.home-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 20px 16px;
}

.greeting-sub {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-bottom: 2px;
}

.greeting-name {
  font-family: 'Syne', sans-serif;
  font-size: 24px;
  font-weight: 800;
  color: var(--color-text);
  letter-spacing: -0.5px;
}

.stats-strip {
  display: flex;
  align-items: center;
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  margin: 0 16px 24px;
  padding: 16px 0;
  box-shadow: var(--shadow-sm);
}

.stat-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.stat-value {
  font-family: 'Syne', sans-serif;
  font-size: 26px;
  font-weight: 800;
  color: var(--color-accent);
  letter-spacing: -1px;
}

.stat-label {
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.stat-divider {
  width: 1px;
  height: 36px;
  background: var(--color-border);
}

.section-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-tertiary);
  letter-spacing: 0.5px;
  text-transform: uppercase;
  padding: 0 20px 12px;
}

.no-modules {
  margin: 8px 16px 32px;
  padding: 32px 16px;
  border-radius: var(--radius-lg);
  background: var(--color-surface);
  text-align: center;
  font-size: 13px;
  color: var(--color-text-tertiary);
  box-shadow: var(--shadow-sm);
}

.modules-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  padding: 0 16px 32px;
}

.module-card {
  background: var(--color-surface);
  border: none;
  border-radius: var(--radius-lg);
  padding: 20px 16px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
  box-shadow: var(--shadow-sm);
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
  text-align: left;
}

.module-card:active {
  transform: scale(0.96);
  box-shadow: none;
}

.module-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
}

.module-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text);
  letter-spacing: -0.2px;
}

.module-desc {
  font-size: 12px;
  color: var(--color-text-tertiary);
  line-height: 1.4;
}
</style>
