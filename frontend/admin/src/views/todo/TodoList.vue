<template>
  <div class="todo-list">
    <div class="list-body">
      <div v-if="store.items.length === 0" class="list-empty">
        <svg viewBox="0 0 48 48" fill="none" width="48" height="48"><rect x="6" y="10" width="36" height="28" rx="4" stroke="currentColor" stroke-width="2"/><path d="M16 22h16M16 30h10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
        <p>暂无事项</p>
      </div>
      <div
        v-for="item in store.items"
        :key="item.id"
        class="item-row"
        :class="['priority-stripe--' + item.priority, { 'item-row--active': store.currentItem?.id === item.id }]"
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
          <div class="item-top">
            <span class="item-title" :class="{ 'item-title--done': item.status === 'completed' }">{{ item.title }}</span>
            <span v-if="item.scheduled_at" class="time-badge time-badge--scheduled">🕐 {{ formatDate(item.scheduled_at) }}</span>
            <span v-else-if="item.due_date" class="time-badge" :class="{ 'time-badge--overdue': isOverdue(item) }">📅 {{ formatDate(item.due_date) }}</span>
          </div>

          <div v-if="item.category_name || item.tags.length || item.importance >= 4" class="item-meta">
            <span v-if="item.category_name" class="meta-category">
              <svg viewBox="0 0 12 12" fill="currentColor" width="9" height="9" style="flex-shrink:0"><path d="M1 3.5A1.5 1.5 0 012.5 2h1.764a1.5 1.5 0 011.06.44L6 3.12l.676-.68A1.5 1.5 0 017.736 2H9.5A1.5 1.5 0 0111 3.5v5A1.5 1.5 0 019.5 10h-7A1.5 1.5 0 011 8.5v-5z"/></svg>
              {{ item.category_name }}
            </span>
            <span
              v-for="tag in item.tags"
              :key="tag.id"
              class="meta-tag"
              :style="{ '--tag-color': tag.color }"
            ><span class="tag-dot"></span>{{ tag.name }}</span>
            <span v-if="item.importance >= 4" class="meta-importance" :class="{ 'meta-importance--5': item.importance === 5 }">
              {{ item.importance === 5 ? '极其重要' : '非常重要' }}
            </span>
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

function formatDate(d) {
  if (!d) return ''
  const date = new Date(d)
  const now = new Date()
  const isThisYear = date.getFullYear() === now.getFullYear()
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric', ...(!isThisYear && { year: 'numeric' }) })
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

/* 行整体 */
.item-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 16px 12px 20px;
  border-bottom: 1px solid var(--color-border-light);
  cursor: pointer;
  transition: background var(--transition-fast);
  border-left: 3px solid transparent;
}

.item-row:hover { background: var(--color-surface-hover); }
.item-row--active { background: var(--color-accent-subtle); }

/* 优先级左边框 — 静默编码，不占额外空间 */
.priority-stripe--1 { border-left-color: transparent; }
.priority-stripe--2 { border-left-color: var(--color-border); }
.priority-stripe--3 { border-left-color: #60a5fa; }
.priority-stripe--4 { border-left-color: var(--color-warning); }
.priority-stripe--5 { border-left-color: var(--color-danger); }

/* 勾选按钮 */
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

.check-circle:hover { border-color: var(--color-accent); }

.check-circle--done {
  background: var(--color-status-completed);
  border-color: var(--color-status-completed);
}

.check-circle--paused {
  border-color: var(--color-status-paused);
  border-style: dashed;
}

/* 内容区 */
.item-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

/* 标题行：标题 + 时间右对齐 */
.item-top {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.item-title {
  flex: 1;
  font-size: 14px;
  color: var(--color-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.4;
}

.item-title--done {
  text-decoration: line-through;
  color: var(--color-text-tertiary);
}

.time-badge {
  font-size: 11px;
  font-weight: 500;
  color: var(--color-text-tertiary);
  white-space: nowrap;
  flex-shrink: 0;
}

.time-badge--scheduled {
  color: var(--color-accent-text);
}

.time-badge--overdue {
  color: var(--color-danger);
}

/* 元数据行：分类 + 标签 + 重要程度 */
.item-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 5px;
}

/* 分类：方角 + 灰色 */
.meta-category {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 11px;
  font-weight: 500;
  color: var(--color-text-secondary);
  background: var(--color-surface-hover);
  padding: 1px 6px;
  border-radius: 4px;
  line-height: 1.6;
}

/* 标签：胶囊 + 彩色 */
.meta-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  font-weight: 500;
  color: var(--tag-color);
  background: color-mix(in srgb, var(--tag-color) 12%, transparent);
  padding: 1px 7px;
  border-radius: var(--radius-pill);
  line-height: 1.6;
}

.tag-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: currentColor;
  flex-shrink: 0;
}

/* 重要程度：只在 4/5 时出现 */
.meta-importance {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-warning);
  background: rgba(217, 119, 6, 0.08);
  padding: 1px 6px;
  border-radius: 4px;
  line-height: 1.6;
}

.meta-importance--5 {
  color: var(--color-danger);
  background: rgba(239, 68, 68, 0.08);
}
</style>
