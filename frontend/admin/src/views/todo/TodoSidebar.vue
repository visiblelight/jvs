<template>
  <div class="todo-sidebar">
    <!-- Status -->
    <div class="section">
      <h3 class="section-label">状态</h3>
      <div class="filter-group">
        <button
          v-for="s in statusOptions"
          :key="s.value"
          class="filter-chip"
          :class="{ active: store.filters.status === s.value }"
          @click="store.setFilter('status', store.filters.status === s.value ? null : s.value)"
        >
          <span class="chip-dot" :style="{ background: s.color }"></span>
          {{ s.label }}
        </button>
      </div>
    </div>

    <!-- Categories -->
    <div class="section">
      <div class="section-head">
        <h3 class="section-label">分类</h3>
        <button class="section-btn" @click="$emit('manage-categories')">
          <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14"><path d="M8 2a.75.75 0 01.75.75v4.5h4.5a.75.75 0 010 1.5h-4.5v4.5a.75.75 0 01-1.5 0v-4.5h-4.5a.75.75 0 010-1.5h4.5v-4.5A.75.75 0 018 2z"/></svg>
        </button>
      </div>
      <div class="tree-list">
        <button
          class="tree-item"
          :class="{ active: store.filters.category_id === null }"
          @click="store.setFilter('category_id', null)"
        >全部</button>
        <template v-for="cat in store.categories" :key="cat.id">
          <button
            class="tree-item"
            :class="{ active: store.filters.category_id === cat.id }"
            @click="store.setFilter('category_id', cat.id)"
          >{{ cat.name }}</button>
          <button
            v-for="child in cat.children"
            :key="child.id"
            class="tree-item tree-item--nested"
            :class="{ active: store.filters.category_id === child.id }"
            @click="store.setFilter('category_id', child.id)"
          >{{ child.name }}</button>
        </template>
      </div>
    </div>

    <!-- Tags -->
    <div class="section">
      <div class="section-head">
        <h3 class="section-label">标签</h3>
        <button class="section-btn" @click="$emit('manage-tags')">
          <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14"><path d="M8 2a.75.75 0 01.75.75v4.5h4.5a.75.75 0 010 1.5h-4.5v4.5a.75.75 0 01-1.5 0v-4.5h-4.5a.75.75 0 010-1.5h4.5v-4.5A.75.75 0 018 2z"/></svg>
        </button>
      </div>
      <div class="tree-list">
        <button
          class="tree-item"
          :class="{ active: store.filters.tag_id === null }"
          @click="store.setFilter('tag_id', null)"
        >全部</button>
        <button
          v-for="tag in store.tags"
          :key="tag.id"
          class="tree-item"
          :class="{ active: store.filters.tag_id === tag.id }"
          @click="store.setFilter('tag_id', store.filters.tag_id === tag.id ? null : tag.id)"
        >
          <span class="chip-dot" :style="{ background: tag.color }"></span>
          {{ tag.name }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useTodoStore } from '@/stores/todo'

defineEmits(['manage-categories', 'manage-tags'])

const store = useTodoStore()

const statusOptions = [
  { value: 'pending', label: '未完成', color: 'var(--color-status-pending)' },
  { value: 'paused', label: '暂停中', color: 'var(--color-status-paused)' },
  { value: 'completed', label: '已完成', color: 'var(--color-status-completed)' },
]
</script>

<style scoped>
.todo-sidebar {
  width: 230px;
  background: var(--color-surface);
  border-right: 1px solid var(--color-border-light);
  overflow-y: auto;
  padding: 20px 0;
  flex-shrink: 0;
}

.section {
  margin-bottom: 24px;
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px 0 20px;
  margin-bottom: 6px;
}

.section-label {
  font-family: var(--font-body);
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.8px;
  margin: 0 0 6px;
  padding: 0 20px;
}

.section-head .section-label {
  padding: 0;
  margin: 0;
}

.section-btn {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: none;
  color: var(--color-text-tertiary);
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.section-btn:hover {
  background: var(--color-surface-hover);
  color: var(--color-accent-text);
}

.filter-group {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding: 0 16px;
}

.filter-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 12px;
  border: 1px solid var(--color-border);
  border-radius: 20px;
  background: none;
  font-family: var(--font-body);
  font-size: 12px;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.filter-chip:hover {
  border-color: var(--color-text-tertiary);
}

.filter-chip.active {
  background: var(--color-accent-subtle);
  border-color: var(--color-accent);
  color: var(--color-accent-text);
}

.chip-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

.tree-list {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.tree-item {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 7px 20px;
  border: none;
  background: none;
  font-family: var(--font-body);
  font-size: 13px;
  color: var(--color-text-secondary);
  cursor: pointer;
  text-align: left;
  transition: all var(--transition-fast);
}

.tree-item:hover {
  background: var(--color-surface-hover);
  color: var(--color-text);
}

.tree-item.active {
  background: var(--color-accent-subtle);
  color: var(--color-accent-text);
}

.tree-item--nested {
  padding-left: 36px;
}
</style>
