<template>
  <Teleport to="body">
    <div v-if="visible" class="archive-overlay" @click.self="handleClose">
      <div class="archive-modal" @click.stop>
        <div class="archive-header">
          <div style="display: flex; align-items: center; gap: 8px;">
            <svg viewBox="0 0 16 16" fill="currentColor" width="18" height="18" style="color: var(--color-text-secondary)">
              <path d="M1.75 2.5h12.5a.25.25 0 01.25.25v1.5a.25.25 0 01-.25.25H1.75a.25.25 0 01-.25-.25v-1.5a.25.25 0 01.25-.25zM0 2.75C0 1.784.784 1 1.75 1h12.5c.966 0 1.75.784 1.75 1.75v1.5A1.75 1.75 0 0114.25 6H1.75A1.75 1.75 0 010 4.25v-1.5zM1.75 7a.75.75 0 00-.75.75v5.5c0 .966.784 1.75 1.75 1.75h10.5A1.75 1.75 0 0015 13.25v-5.5a.75.75 0 00-1.5 0v5.5a.25.25 0 01-.25.25H2.75a.25.25 0 01-.25-.25v-5.5A.75.75 0 001.75 7zM6 9.25a.75.75 0 01.75-.75h2.5a.75.75 0 010 1.5h-2.5a.75.75 0 01-.75-.75z"/>
            </svg>
            <h2>归档 / 已归档事项</h2>
          </div>
          <button class="archive-close-btn" @click="handleClose">&times;</button>
        </div>

        <div class="archive-body">
          <div v-if="loading" class="archive-empty">
            <p>正在加载...</p>
          </div>
          <div v-else-if="items.length === 0" class="archive-empty">
            <p>暂无归档事项</p>
          </div>
          <div v-else class="archive-list">
            <div v-for="item in items" :key="item.id" class="archive-item">
              <div class="archive-item-info">
                <h4>{{ item.title }}</h4>
                <span class="archive-item-date">归档于: {{ formatDate(item.archived_at) }}</span>
              </div>
              <div class="archive-item-actions">
                <button class="btn-unarchive" @click="unarchiveItem(item.id)">取消归档</button>
                <button class="btn-hard-delete" @click="hardDeleteContent(item.id)">永久删除</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, watch } from 'vue'
import { getItems, updateItemStatus, hardDeleteItem } from '@/api/todo'
import { useTodoStore } from '@/stores/todo'

const visible = defineModel('visible', { type: Boolean, default: false })

const store = useTodoStore()
const items = ref([])
const loading = ref(false)

async function fetchArchived() {
  loading.value = true
  try {
    const { data } = await getItems({ status: 'archived', page_size: 100 })
    items.value = data.items
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

watch(visible, (newVal) => {
  if (newVal) {
    fetchArchived()
  }
})

async function unarchiveItem(id) {
  try {
    await updateItemStatus(id, 'completed')
    await fetchArchived()
    store.fetchItems()
  } catch (e) {
    console.error(e)
  }
}

async function hardDeleteContent(id) {
  if (!confirm('确认永久删除该事项吗？此操作不可逆！')) return
  try {
    await hardDeleteItem(id)
    await fetchArchived()
  } catch (e) {
    console.error(e)
  }
}

function handleClose() {
  visible.value = false
}

function formatDate(ds) {
  if (!ds) return '未知时间'
  const d = new Date(ds)
  return `${d.toLocaleDateString()} ${d.toLocaleTimeString()}`
}
</script>

<style scoped>
.archive-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.archive-modal {
  width: 600px;
  max-width: 90vw;
  max-height: 80vh;
  background: var(--color-bg-base);
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-xl);
  overflow: hidden;
  animation: archiveScaleIn 0.2s cubic-bezier(0.3, 1.2, 0.2, 1);
}

@keyframes archiveScaleIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

.archive-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--color-border-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--color-surface);
}

.archive-header h2 {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: var(--color-text);
  font-family: var(--font-heading);
}

.archive-close-btn {
  background: none;
  border: none;
  font-size: 24px;
  line-height: 1;
  color: var(--color-text-secondary);
  cursor: pointer;
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}
.archive-close-btn:hover {
  color: var(--color-text);
  background: var(--color-surface-hover);
}

.archive-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.archive-empty {
  text-align: center;
  color: var(--color-text-tertiary);
  padding: 40px 0;
  font-family: var(--font-body);
}

.archive-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.archive-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--color-surface);
  border: 1px solid var(--color-border-light);
  padding: 12px 16px;
  border-radius: var(--radius-md);
  transition: border-color var(--transition-fast);
}

.archive-item:hover {
  border-color: var(--color-border);
}

.archive-item-info h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
  color: var(--color-text);
  font-family: var(--font-body);
}

.archive-item-date {
  font-size: 11px;
  color: var(--color-text-tertiary);
  font-family: var(--font-mono, monospace);
}

.archive-item-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.btn-unarchive {
  background: var(--color-surface-hover);
  border: 1px solid var(--color-border);
  color: var(--color-text);
  padding: 6px 12px;
  border-radius: var(--radius-pill);
  font-size: 12px;
  cursor: pointer;
  transition: all var(--transition-fast);
}
.btn-unarchive:hover {
  border-color: var(--color-accent);
  color: var(--color-accent-text);
  background: var(--color-accent-subtle);
}

.btn-hard-delete {
  background: var(--color-danger-subtle, rgba(239, 68, 68, 0.15));
  border: 1px solid transparent;
  color: var(--color-danger);
  padding: 6px 12px;
  border-radius: var(--radius-pill);
  font-size: 12px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-hard-delete:hover {
  background: var(--color-danger);
  color: white;
}
</style>
