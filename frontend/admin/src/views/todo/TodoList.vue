<template>
  <div class="todo-list">
    <div class="list-header">
      <div class="header-info">
        <h2 class="list-title">事项</h2>
        <span class="list-count">{{ store.total }}</span>
      </div>
      <button class="btn-create" @click="$emit('create')">
        <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14"><path d="M8 2a.75.75 0 01.75.75v4.5h4.5a.75.75 0 010 1.5h-4.5v4.5a.75.75 0 01-1.5 0v-4.5h-4.5a.75.75 0 010-1.5h4.5v-4.5A.75.75 0 018 2z"/></svg>
        新建
      </button>
    </div>
    <div class="list-body">
      <div v-if="store.items.length === 0" class="list-empty">
        <svg viewBox="0 0 48 48" fill="none" width="48" height="48"><rect x="6" y="10" width="36" height="28" rx="4" stroke="currentColor" stroke-width="2"/><path d="M16 22h16M16 30h10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
        <p>暂无事项</p>
      </div>
      <div
        v-for="item in store.items"
        :key="item.id"
        class="item-row"
        :class="{ 'item-row--active': store.currentItem?.id === item.id }"
        @click="store.selectItem(item.id)"
      >
        <button class="check-btn" @click.stop="toggleStatus(item)" :disabled="store.filters.is_deleted">
          <span
            class="check-circle"
            :class="{
              'check-circle--done': item.status === 'completed',
              'check-circle--paused': item.status === 'paused',
              'check-circle--disabled': store.filters.is_deleted
            }"
          >
            <svg v-if="item.status === 'completed'" viewBox="0 0 12 12" fill="none" width="10" height="10"><path d="M2.5 6l2.5 2.5 4.5-4.5" stroke="white" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </span>
        </button>
        <div class="item-content">
          <div class="item-title" :class="{ 'item-title--done': item.status === 'completed' }">
            {{ item.title }}
          </div>
          <div class="item-badges">
            <span class="badge badge--priority" :class="'priority-' + item.priority">{{ getPriorityLabel(item.priority) }}</span>
            <span class="badge badge--importance">{{ getImportanceLabel(item.importance) }}</span>
            <span v-if="item.due_date" class="badge badge--due" :class="{ overdue: isOverdue(item) }">{{ formatDate(item.due_date) }}</span>
            <span
              v-for="tag in item.tags"
              :key="tag.id"
              class="badge badge--tag"
              :style="{ '--tag-color': tag.color }"
            >{{ tag.name }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useTodoStore } from '@/stores/todo'
import { updateItemStatus } from '@/api/todo'

defineEmits(['create'])

const store = useTodoStore()

const priorities = ['极低', '低', '中等', '高', '极高']
const importances = ['不重要', '一般', '偏重要', '非常重要', '极其重要']
const getPriorityLabel = (n) => priorities[n - 1] || '无'
const getImportanceLabel = (n) => importances[n - 1] || '无'

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

function isOverdue(item) {
  return item.due_date && item.status !== 'completed' && new Date(item.due_date) < new Date()
}

async function toggleStatus(item) {
  const nextStatus = item.status === 'completed' ? 'pending' : 'completed'
  await updateItemStatus(item.id, nextStatus)
  store.fetchItems()
  if (store.currentItem?.id === item.id) {
    store.selectItem(item.id)
  }
}
</script>

<style scoped>
.todo-list {
  flex: 1;
  min-width: 340px;
  background: var(--color-surface);
  border-right: 1px solid var(--color-border-light);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--color-border-light);
  flex-shrink: 0;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.list-title {
  font-family: var(--font-heading);
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.list-count {
  font-size: 12px;
  font-weight: 500;
  color: var(--color-text-tertiary);
  background: var(--color-surface-hover);
  padding: 2px 8px;
  border-radius: 10px;
}

.btn-create {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 18px;
  background: var(--color-accent);
  color: white;
  border: none;
  border-radius: var(--radius-pill);
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-create:hover {
  background: var(--color-accent-hover);
  transform: translateY(-1px);
}

.list-body {
  flex: 1;
  overflow-y: auto;
}

.list-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--color-text-tertiary);
  gap: 12px;
}

.list-empty p {
  font-size: 14px;
}

.item-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 20px;
  border-bottom: 1px solid var(--color-border-light);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.item-row:hover {
  background: var(--color-surface-hover);
}

.item-row--active {
  background: var(--color-accent-subtle);
}

.check-btn {
  padding: 2px 0 0;
  border: none;
  background: none;
  cursor: pointer;
  flex-shrink: 0;
}

.check-circle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 2px solid var(--color-border);
  transition: all var(--transition-fast);
}

.check-circle:hover {
  border-color: var(--color-accent);
}

.check-circle--done {
  background: var(--color-status-completed);
  border-color: var(--color-status-completed);
}

.check-circle--paused {
  border-color: var(--color-status-paused);
  border-style: dashed;
}

.item-content {
  flex: 1;
  min-width: 0;
}

.item-title {
  font-size: 14px;
  color: var(--color-text);
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.3;
}

.item-title--done {
  text-decoration: line-through;
  color: var(--color-text-tertiary);
}

.item-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.badge {
  font-size: 11px;
  font-weight: 500;
  padding: 1px 7px;
  border-radius: 4px;
  line-height: 1.6;
}

.badge--priority {
  background: var(--color-surface-hover);
  color: var(--color-text-tertiary);
}

.badge--priority.priority-4,
.badge--priority.priority-5 {
  background: rgba(217, 119, 6, 0.1);
  color: var(--color-warning);
}

.badge--importance {
  background: var(--color-surface-hover);
  color: var(--color-text-tertiary);
}

.badge--due {
  color: var(--color-text-tertiary);
}

.badge--due.overdue {
  color: var(--color-danger);
}

.badge--tag {
  background: color-mix(in srgb, var(--tag-color) 12%, transparent);
  color: var(--tag-color);
}
</style>
