<template>
  <div class="todo-page">
    <PageHeader title="事项" back-to="/home">
      <template #right>
        <button class="filter-btn" @click="showFilter = true">
          <svg viewBox="0 0 24 24" fill="none" width="18" height="18">
            <path d="M3 6h18M7 12h10M11 18h2" stroke="currentColor" stroke-width="2"
              stroke-linecap="round"/>
          </svg>
          <span v-if="hasFilter" class="filter-dot" />
        </button>
      </template>
    </PageHeader>

    <div class="tab-strip">
      <button
        v-for="tab in statusTabs"
        :key="tab.value"
        class="tab-btn"
        :class="{ active: store.filters.status === tab.value }"
        @click="store.setFilter('status', tab.value)"
      >{{ tab.label }}</button>
    </div>

    <div class="list-area" ref="listEl">
      <div v-if="store.loading && !store.items.length" class="list-loading">
        <div class="spinner" />
      </div>

      <div v-else-if="!store.items.length" class="list-empty">
        <svg viewBox="0 0 48 48" fill="none" width="48" height="48">
          <rect x="8" y="6" width="32" height="36" rx="3" stroke="currentColor" stroke-width="1.5"/>
          <path d="M16 18h16M16 26h10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        <p>暂无事项</p>
      </div>

      <div v-else class="item-list">
        <div
          v-for="item in store.items"
          :key="item.id"
          class="todo-item"
          :class="{ done: item.status === 'completed' }"
        >
          <button class="check-btn" @click="toggleDone(item)">
            <svg v-if="item.status === 'completed'" viewBox="0 0 24 24" fill="none" width="20" height="20">
              <circle cx="12" cy="12" r="10" fill="var(--color-accent)"/>
              <path d="M7 12l4 4 6-7" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" width="20" height="20">
              <circle cx="12" cy="12" r="10" stroke="var(--color-border)" stroke-width="2"/>
            </svg>
          </button>

          <div class="item-content" @click="openEdit(item)">
            <div class="item-title">{{ item.title }}</div>
            <div class="item-meta">
              <span v-if="item.category_name" class="meta-category">{{ item.category_name }}</span>
              <span v-for="tag in item.tags" :key="tag.id" class="meta-tag" :style="{ '--tag-color': tag.color }">{{ tag.name }}</span>
              <span v-if="item.importance >= 4" class="meta-importance" :class="{ critical: item.importance === 5 }">
                {{ item.importance === 5 ? '极重要' : '重要' }}
              </span>
              <span v-if="item.scheduled_at" class="meta-due">🕐 {{ formatDate(item.scheduled_at) }}</span>
              <span v-else-if="item.due_date" class="meta-due"
                :class="{ overdue: isOverdue(item.due_date) && item.status !== 'completed' }">
                {{ formatDate(item.due_date) }}
              </span>
            </div>
          </div>

          <button class="delete-btn" @click="handleDelete(item)">
            <svg viewBox="0 0 24 24" fill="none" width="16" height="16">
              <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- FAB -->
    <button class="fab" @click="openCreate">
      <svg viewBox="0 0 24 24" fill="none" width="24" height="24">
        <path d="M12 5v14M5 12h14" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
      </svg>
    </button>

    <!-- Filter Sheet -->
    <BottomSheet v-model="showFilter" title="筛选">
      <div class="filter-body">
        <div class="filter-section">
          <p class="filter-label">优先级</p>
          <div class="filter-chips">
            <button
              v-for="p in priorityOptions"
              :key="p.value"
              class="chip"
              :class="{ active: store.filters.priority === p.value }"
              @click="store.setFilter('priority', store.filters.priority === p.value ? null : p.value)"
            >{{ p.label }}</button>
          </div>
        </div>
        <div class="filter-section">
          <p class="filter-label">分类</p>
          <div class="filter-chips">
            <button
              v-for="c in store.categories"
              :key="c.id"
              class="chip"
              :class="{ active: store.filters.category_id === c.id }"
              @click="store.setFilter('category_id', store.filters.category_id === c.id ? null : c.id)"
            >{{ c.name }}</button>
          </div>
        </div>
        <button class="reset-btn" @click="store.resetFilters(); showFilter = false">清除筛选</button>
      </div>
    </BottomSheet>

    <!-- Form Sheet -->
    <TodoFormSheet v-model="showForm" :item="editItem" @saved="onSaved" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useTodoStore } from '@/stores/todo'
import * as api from '@/api/todo'
import PageHeader from '@/components/PageHeader.vue'
import BottomSheet from '@/components/BottomSheet.vue'
import TodoFormSheet from './TodoFormSheet.vue'

const store = useTodoStore()
const showFilter = ref(false)
const showForm = ref(false)
const editItem = ref(null)

const statusTabs = [
  { label: '全部', value: null },
  { label: '未完成', value: 'pending' },
  { label: '已完成', value: 'completed' },
]

const priorityOptions = [
  { label: '高', value: 4 },
  { label: '中', value: 3 },
  { label: '低', value: 2 },
]

const priorityLabels = { 1: '极低', 2: '低', 3: '中', 4: '高', 5: '极高' }

const hasFilter = computed(() =>
  store.filters.priority !== null || store.filters.category_id !== null
)

function openCreate() { editItem.value = null; showForm.value = true }
function openEdit(item) { editItem.value = item; showForm.value = true }

function onSaved() { store.fetchItems() }

async function toggleDone(item) {
  await api.updateItem(item.id, { status: item.status === 'completed' ? 'pending' : 'completed' })
  store.fetchItems()
}

async function handleDelete(item) {
  if (!confirm(`删除"${item.title}"？`)) return
  await api.deleteItem(item.id)
  store.fetchItems()
}

function isOverdue(date) {
  return date && new Date(date) < new Date()
}

function formatDate(d) {
  if (!d) return ''
  const date = new Date(d)
  const now = new Date()
  const diff = Math.ceil((date - now) / 86400000)
  if (diff === 0) return '今天'
  if (diff === 1) return '明天'
  if (diff < 0) return `逾期 ${-diff} 天`
  return `${date.getMonth() + 1}/${date.getDate()}`
}

onMounted(() => {
  store.fetchCategories()
  store.fetchTags()
  store.fetchItems()
})
</script>

<style scoped>
.todo-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--color-bg);
  position: relative;
}

.tab-strip {
  display: flex;
  gap: 4px;
  padding: 12px 16px 8px;
  flex-shrink: 0;
}

.tab-btn {
  padding: 7px 16px;
  border: none;
  background: none;
  font-size: 14px;
  color: var(--color-text-tertiary);
  border-radius: var(--radius-full);
  transition: all var(--transition-fast);
  font-weight: 500;
}

.tab-btn.active {
  background: var(--color-accent-subtle);
  color: var(--color-accent-text);
  font-weight: 600;
}

.filter-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: none;
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.filter-dot {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 7px;
  height: 7px;
  background: var(--color-accent);
  border-radius: 50%;
}

.list-area {
  flex: 1;
  overflow-y: auto;
  padding: 0 0 100px;
}

.list-loading, .list-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 64px 24px;
  gap: 12px;
  color: var(--color-text-tertiary);
  font-size: 14px;
}

.spinner {
  width: 28px;
  height: 28px;
  border: 2.5px solid var(--color-border);
  border-top-color: var(--color-accent);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.item-list { padding: 4px 0; }

.todo-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border-light);
  transition: background var(--transition-fast);
}

.todo-item.done .item-title { text-decoration: line-through; color: var(--color-text-tertiary); }

.check-btn { border: none; background: none; flex-shrink: 0; display: flex; align-items: center; }

.item-content { flex: 1; min-width: 0; }

.item-title {
  font-size: 15px;
  color: var(--color-text);
  margin-bottom: 5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-meta { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }

.meta-category {
  font-size: 11px;
  padding: 1px 8px;
  background: var(--color-bg);
  color: var(--color-text-secondary);
  border-radius: 4px;
  font-weight: 500;
}

.meta-tag {
  font-size: 11px;
  padding: 1px 8px;
  background: color-mix(in srgb, var(--tag-color) 12%, transparent);
  color: var(--tag-color);
  border-radius: var(--radius-full);
}

.meta-importance {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-warning);
}
.meta-importance.critical { color: var(--color-danger); }

.meta-due { font-size: 12px; color: var(--color-text-tertiary); }
.meta-due.overdue { color: var(--color-danger); }

.delete-btn {
  border: none;
  background: none;
  color: var(--color-text-tertiary);
  padding: 8px;
  flex-shrink: 0;
}

.fab {
  position: absolute;
  right: 20px;
  bottom: 24px;
  width: 56px;
  height: 56px;
  background: var(--color-accent);
  border: none;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 16px rgba(79,70,229,0.4);
  transition: transform var(--transition-fast);
  z-index: 10;
}
.fab:active { transform: scale(0.93); }

/* Filter sheet */
.filter-body { display: flex; flex-direction: column; gap: 20px; }
.filter-section { display: flex; flex-direction: column; gap: 10px; }
.filter-label { font-size: 13px; font-weight: 600; color: var(--color-text-secondary); }
.filter-chips { display: flex; flex-wrap: wrap; gap: 8px; }

.chip {
  padding: 7px 16px;
  border: 1.5px solid var(--color-border);
  background: none;
  border-radius: var(--radius-full);
  font-size: 14px;
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
}
.chip.active {
  border-color: var(--color-accent);
  background: var(--color-accent-subtle);
  color: var(--color-accent-text);
  font-weight: 500;
}

.reset-btn {
  padding: 12px;
  border: 1.5px solid var(--color-border);
  background: none;
  border-radius: var(--radius-md);
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-top: 4px;
}
</style>
