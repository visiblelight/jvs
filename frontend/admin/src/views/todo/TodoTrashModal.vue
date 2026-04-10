<template>
  <Teleport to="body">
    <div v-if="visible" class="trash-overlay" @click.self="handleClose">
      <div class="trash-modal" @click.stop>
        <div class="trash-header">
          <div style="display: flex; align-items: center; gap: 8px;">
            <svg viewBox="0 0 16 16" fill="currentColor" width="18" height="18" style="color: var(--color-danger)">
              <path d="M6.5 1.75a.25.25 0 01.25-.25h2.5a.25.25 0 01.25.25V3h-3V1.75zm4.5 0V3h2.25a.75.75 0 010 1.5H2.75a.75.75 0 010-1.5H5V1.75C5 .784 5.784 0 6.75 0h2.5C10.216 0 11 .784 11 1.75zM4.496 6.675a.75.75 0 10-1.492.15l.66 6.6A1.75 1.75 0 005.405 15h5.19a1.75 1.75 0 001.741-1.575l.66-6.6a.75.75 0 00-1.492-.15l-.66 6.6a.25.25 0 01-.249.225h-5.19a.25.25 0 01-.249-.225l-.66-6.6z"/>
            </svg>
            <h2>垃圾桶 / 已删除事项</h2>
          </div>
          <button class="trash-close-btn" @click="handleClose">×</button>
        </div>

        <div class="trash-body">
          <div v-if="loading" class="trash-empty">
            <p>正在加载...</p>
          </div>
          <div v-else-if="items.length === 0" class="trash-empty">
            <p>垃圾桶空空如也~</p>
          </div>
          <div v-else class="trash-list">
            <div v-for="item in items" :key="item.id" class="trash-item">
              <div class="trash-item-info">
                <h4>{{ item.title }}</h4>
                <span class="trash-item-date">删除于: {{ formatDate(item.deleted_at) }}</span>
              </div>
              <div class="trash-item-actions">
                <button class="btn-restore" @click="restoreContent(item.id)">恢复</button>
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
import { useDialog } from '@/composables/useDialog'
const { confirm } = useDialog()
import { getItems, restoreItem, hardDeleteItem } from '@/api/todo'
import { useTodoStore } from '@/stores/todo'

const visible = defineModel('visible', { type: Boolean, default: false })

const store = useTodoStore()
const items = ref([])
const loading = ref(false)

async function fetchDeleted() {
  loading.value = true
  try {
    const { data } = await getItems({ is_deleted: true, skip: 0, limit: 100 })
    items.value = data.items
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

watch(visible, (newVal) => {
  if (newVal) {
    fetchDeleted()
  }
})

async function restoreContent(id) {
  try {
    await restoreItem(id)
    await fetchDeleted()
    store.fetchItems()
  } catch (e) {
    console.error(e)
  }
}

async function hardDeleteContent(id) {
  if (!await confirm('确认永久删除该事项吗？此操作不可逆！', { title: '永久删除', danger: true })) return
  try {
    await hardDeleteItem(id)
    await fetchDeleted()
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
.trash-overlay {
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

.trash-modal {
  width: 600px;
  max-width: 90vw;
  max-height: 80vh;
  background: var(--color-bg-base);
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-xl);
  overflow: hidden;
  animation: trashScaleIn 0.2s cubic-bezier(0.3, 1.2, 0.2, 1);
}

@keyframes trashScaleIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

.trash-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--color-border-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--color-surface);
}

.trash-header h2 {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: var(--color-text);
  font-family: var(--font-heading);
}

.trash-close-btn {
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
.trash-close-btn:hover {
  color: var(--color-text);
  background: var(--color-surface-hover);
}

.trash-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.trash-empty {
  text-align: center;
  color: var(--color-text-tertiary);
  padding: 40px 0;
  font-family: var(--font-body);
}

.trash-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.trash-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--color-surface);
  border: 1px solid var(--color-border-light);
  padding: 12px 16px;
  border-radius: var(--radius-md);
  transition: border-color var(--transition-fast);
}

.trash-item:hover {
  border-color: var(--color-border);
}

.trash-item-info h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
  color: var(--color-text);
  font-family: var(--font-body);
}

.trash-item-date {
  font-size: 11px;
  color: var(--color-text-tertiary);
  font-family: var(--font-mono, monospace);
}

.trash-item-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.btn-restore {
  background: var(--color-surface-hover);
  border: 1px solid var(--color-border);
  color: var(--color-text);
  padding: 6px 12px;
  border-radius: var(--radius-pill);
  font-size: 12px;
  cursor: pointer;
  transition: all var(--transition-fast);
}
.btn-restore:hover {
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
