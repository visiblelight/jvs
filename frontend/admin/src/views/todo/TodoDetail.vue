<template>
  <div class="todo-detail" v-if="store.currentItem">
    <div class="detail-header">
      <h3 class="detail-title">{{ store.currentItem.title }}</h3>
      <div class="detail-actions">
          <button class="act-btn act-btn--edit" @click="$emit('edit', store.currentItem)">
            <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14"><path d="M11.013 1.427a1.75 1.75 0 012.474 0l1.086 1.086a1.75 1.75 0 010 2.474l-8.61 8.61c-.21.21-.47.364-.756.445l-3.251.93a.75.75 0 01-.927-.928l.929-3.25a1.75 1.75 0 01.445-.758l8.61-8.61zm1.414 1.06a.25.25 0 00-.354 0L3.463 11.098a.25.25 0 00-.064.108l-.558 1.953 1.953-.558a.25.25 0 00.108-.064l8.61-8.61a.25.25 0 000-.354l-1.086-1.086z"/></svg>
            编辑
          </button>
          <button class="act-btn act-btn--danger" @click="handleDelete">
            <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14"><path d="M6.5 1.75a.25.25 0 01.25-.25h2.5a.25.25 0 01.25.25V3h-3V1.75zm4.5 0V3h2.25a.75.75 0 010 1.5H2.75a.75.75 0 010-1.5H5V1.75C5 .784 5.784 0 6.75 0h2.5C10.216 0 11 .784 11 1.75zM4.496 6.675a.75.75 0 10-1.492.15l.66 6.6A1.75 1.75 0 005.405 15h5.19a1.75 1.75 0 001.741-1.575l.66-6.6a.75.75 0 00-1.492-.15l-.66 6.6a.25.25 0 01-.249.225h-5.19a.25.25 0 01-.249-.225l-.66-6.6z"/></svg>
            删除
          </button>
      </div>
    </div>

    <div class="detail-body">
      <div class="prop">
        <span class="prop-label">状态</span>
        <select class="prop-select" :value="store.currentItem.status" @change="handleStatusChange">
          <option value="pending">未完成</option>
          <option value="paused">暂停中</option>
          <option value="completed">已完成</option>
        </select>
      </div>

      <div class="prop">
        <span class="prop-label">优先级</span>
        <div class="level-dots">
          <span class="detail-badge" :class="'priority-' + store.currentItem.priority">{{ getPriorityLabel(store.currentItem.priority) }}</span>
        </div>
      </div>

      <div class="prop">
        <span class="prop-label">重要程度</span>
        <div class="level-dots">
          <span class="detail-badge">{{ getImportanceLabel(store.currentItem.importance) }}</span>
        </div>
      </div>

      <div class="prop">
        <span class="prop-label">截止时间</span>
        <span class="prop-value" :class="{ overdue: isOverdue }">{{ formatDate(store.currentItem.due_date) || '—' }}</span>
      </div>

      <div class="prop">
        <span class="prop-label">创建时间</span>
        <span class="prop-value">{{ formatDate(store.currentItem.created_at) }}</span>
      </div>

      <div v-if="store.currentItem.completed_at" class="prop">
        <span class="prop-label">完成时间</span>
        <span class="prop-value">{{ formatDate(store.currentItem.completed_at) }}</span>
      </div>

      <div class="prop" v-if="store.currentItem.tags.length">
        <span class="prop-label">标签</span>
        <div class="detail-tags">
          <span
            v-for="tag in store.currentItem.tags"
            :key="tag.id"
            class="detail-tag"
            :style="{ '--tag-color': tag.color }"
          >{{ tag.name }}</span>
        </div>
      </div>

      <div class="desc-section" v-if="store.currentItem.description">
        <span class="prop-label">描述</span>
        <div class="desc-block">{{ store.currentItem.description }}</div>
      </div>
    </div>

    <!-- Custom Confirm Modal -->
    <Teleport to="body">
      <div v-if="confirmDialog.show" class="modal-overlay" @click.self="cancelConfirm">
        <div class="confirm-modal active-scale" @click.stop>
          <div class="confirm-body">
            <h3>确认删除</h3>
            <p>{{ confirmDialog.message }}</p>
          </div>
          <div class="confirm-foot">
            <button class="btn-cancel active-scale" @click="cancelConfirm">取消</button>
            <button class="btn-danger active-scale" @click="executeConfirm">确认删除</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
  <div class="todo-detail todo-detail--empty" v-else>
    <svg viewBox="0 0 48 48" fill="none" width="40" height="40"><circle cx="24" cy="24" r="20" stroke="currentColor" stroke-width="1.5"/><path d="M18 24h12M24 18v12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
    <p>选择一个事项查看详情</p>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useTodoStore } from '@/stores/todo'
import { updateItemStatus, deleteItem } from '@/api/todo'

defineEmits(['edit'])

const store = useTodoStore()

const priorities = ['极低', '低', '中等', '高', '极高']
const importances = ['不重要', '一般', '偏重要', '非常重要', '极其重要']
const getPriorityLabel = (n) => priorities[n - 1] || '无'
const getImportanceLabel = (n) => importances[n - 1] || '无'

// --- Custom Confirm Modal Logic ---
const confirmDialog = ref({
  show: false,
  message: '',
  actionCb: null
})

function customConfirm(message, callback) {
  confirmDialog.value = {
    show: true,
    message,
    actionCb: callback
  }
}

function executeConfirm() {
  if (confirmDialog.value.actionCb) {
    confirmDialog.value.actionCb()
  }
  confirmDialog.value.show = false
}

function cancelConfirm() {
  confirmDialog.value.show = false
}

const isOverdue = computed(() => {
  const item = store.currentItem
  return item?.due_date && item.status !== 'completed' && new Date(item.due_date) < new Date()
})

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleString('zh-CN', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

async function handleStatusChange(e) {
  await updateItemStatus(store.currentItem.id, e.target.value)
  await store.fetchItems()
  await store.selectItem(store.currentItem.id)
}

function handleDelete() {
  customConfirm(`确认将事项「${store.currentItem.title}」移至垃圾桶吗？您可以在垃圾桶找回它。`, async () => {
    await deleteItem(store.currentItem.id)
    store.currentItem = null
    await store.fetchItems()
  })
}
</script>

<style scoped>
.todo-detail {
  width: 360px;
  background: var(--color-surface);
  overflow-y: auto;
  flex-shrink: 0;
}

.todo-detail--empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--color-text-tertiary);
  gap: 12px;
  font-size: 14px;
}

.detail-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 20px;
  border-bottom: 1px solid var(--color-border-light);
  gap: 12px;
}

.detail-title {
  font-family: var(--font-heading);
  font-size: 17px;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
  flex: 1;
  word-break: break-word;
  line-height: 1.4;
}

.detail-actions {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

.act-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 6px 14px;
  border: 1px solid var(--color-border);
  background: none;
  border-radius: var(--radius-pill);
  font-family: var(--font-body);
  font-size: 12px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.act-btn--edit {
  color: var(--color-accent-text);
}

.act-btn--edit:hover {
  border-color: var(--color-accent);
  background: var(--color-accent-subtle);
}

.act-btn--danger {
  color: var(--color-danger);
}

.act-btn--danger:hover {
  border-color: var(--color-danger);
  background: rgba(220, 38, 38, 0.06);
}

.detail-body {
  padding: 20px;
}

.prop {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  font-size: 13px;
}

.prop-label {
  width: 80px;
  color: var(--color-text-tertiary);
  font-weight: 500;
  flex-shrink: 0;
}

.prop-value {
  color: var(--color-text);
}

.prop-value.overdue {
  color: var(--color-danger);
}

.prop-select {
  padding: 6px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-text);
  font-family: var(--font-body);
  font-size: 13px;
  outline: none;
  transition: border-color var(--transition-fast);
}

.prop-select:focus {
  border-color: var(--color-accent);
}

.level-dots {
  display: flex;
  align-items: center;
  gap: 4px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-border);
  transition: background var(--transition-fast);
}

.dot.filled {
  background: var(--color-accent);
}

.level-num {
  margin-left: 6px;
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.detail-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.detail-tag {
  padding: 3px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  background: color-mix(in srgb, var(--tag-color) 12%, transparent);
  color: var(--tag-color);
}

.desc-section {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--color-border-light);
}

.desc-block {
  margin-top: 8px;
  font-size: 13px;
  color: var(--color-text-secondary);
  line-height: 1.7;
  white-space: pre-wrap;
  background: var(--color-bg);
  padding: 12px 16px;
  border-radius: var(--radius-md);
}

.detail-badge {
  font-size: 11px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 4px;
  background: var(--color-surface-hover);
  color: var(--color-text-tertiary);
}

.detail-badge.priority-4,
.detail-badge.priority-5 {
  background: rgba(217, 119, 6, 0.1);
  color: var(--color-warning);
}

/* --- Confirm Modal --- */
.confirm-modal {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  width: 380px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  box-shadow: var(--shadow-lg);
  animation: scaleIn 0.2s cubic-bezier(0.3, 1.2, 0.2, 1);
  margin: auto;
}

@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

.confirm-body h3 {
  font-family: var(--font-heading);
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 12px 0;
  color: var(--color-text);
}

.confirm-body p {
  font-size: 13px;
  color: var(--color-text-secondary);
  line-height: 1.5;
  margin: 0;
}

.confirm-foot {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn-cancel {
  padding: 8px 20px;
  border: 1px solid var(--color-border);
  background: var(--color-bg-base);
  color: var(--color-text-secondary);
  border-radius: var(--radius-pill);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-cancel:hover {
  color: var(--color-text);
  background: rgba(0,0,0,0.05);
}

.btn-danger {
  padding: 8px 20px;
  border: none;
  background: var(--color-danger);
  color: white;
  border-radius: var(--radius-pill);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-danger:hover {
  background: #DC2626; /* darker red */
}
</style>
