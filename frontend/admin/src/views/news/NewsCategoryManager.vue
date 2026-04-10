<template>
  <Teleport to="body">
    <div class="overlay" @click.self="$emit('close')">
      <div class="modal" @click.stop>
        <div class="modal-head">
          <h3>分类管理</h3>
          <button class="close-btn" @click="$emit('close')">
            <svg viewBox="0 0 16 16" fill="currentColor" width="16" height="16"><path d="M3.72 3.72a.75.75 0 011.06 0L8 6.94l3.22-3.22a.75.75 0 111.06 1.06L9.06 8l3.22 3.22a.75.75 0 11-1.06 1.06L8 9.06l-3.22 3.22a.75.75 0 01-1.06-1.06L6.94 8 3.72 4.78a.75.75 0 010-1.06z"/></svg>
          </button>
        </div>

        <div class="modal-body">
          <div class="add-row">
            <input v-model="newName" placeholder="新分类名称" @keyup.enter="handleAdd" />
            <input v-model.number="newSortOrder" type="number" placeholder="排序" style="width: 80px" />
            <button class="btn-primary-sm" @click="handleAdd">添加</button>
          </div>

          <div class="cat-list">
            <div v-for="cat in store.categories" :key="cat.id" class="cat-row">
              <span v-if="editingId !== cat.id" class="cat-name">{{ cat.name }}</span>
              <input v-else v-model="editingName" class="inline-edit" @keyup.enter="saveEdit(cat.id)" />
              <div class="row-actions">
                <button v-if="editingId !== cat.id" class="link-btn" @click="startEdit(cat)">编辑</button>
                <button v-else class="link-btn" @click="saveEdit(cat.id)">保存</button>
                <button class="link-btn link-btn--danger" @click="handleDelete(cat.id)">删除</button>
              </div>
            </div>
            <div v-if="store.categories.length === 0" class="empty">暂无分类</div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'
import { useDialog } from '@/composables/useDialog'
const { toast, confirm } = useDialog()
import { useNewsStore } from '@/stores/news'
import { createCategory, updateCategory, deleteCategory } from '@/api/news'

defineEmits(['close'])
const store = useNewsStore()

const newName = ref('')
const newSortOrder = ref(0)
const editingId = ref(null)
const editingName = ref('')

async function handleAdd() {
  if (!newName.value.trim()) return
  await createCategory({ name: newName.value.trim(), sort_order: newSortOrder.value })
  newName.value = ''
  newSortOrder.value = 0
  await store.fetchCategories()
}

function startEdit(cat) {
  editingId.value = cat.id
  editingName.value = cat.name
}

async function saveEdit(id) {
  if (!editingName.value.trim()) return
  await updateCategory(id, { name: editingName.value.trim() })
  editingId.value = null
  await store.fetchCategories()
}

async function handleDelete(id) {
  if (!await confirm('确定要删除这个分类吗？', { title: '删除分类', danger: true })) return
  try {
    await deleteCategory(id)
    await store.fetchCategories()
  } catch (e) {
    toast(e.response?.data?.detail || '删除失败')
  }
}
</script>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  animation: fadeIn 0.15s ease;
}

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.modal {
  background: var(--color-surface);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-xl);
  width: 480px;
  max-height: 70vh;
  overflow-y: auto;
  box-shadow: var(--shadow-overlay);
  animation: slideUp 0.2s ease;
}

@keyframes slideUp { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }

.modal-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--color-border-light);
}

.modal-head h3 {
  font-family: var(--font-heading);
  font-size: 17px;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.close-btn {
  width: 28px;
  height: 28px;
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

.close-btn:hover {
  background: var(--color-surface-hover);
  color: var(--color-text);
}

.modal-body {
  padding: 20px 24px 24px;
}

.add-row {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.add-row input {
  flex: 1;
  padding: 9px 14px;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-md);
  font-family: var(--font-body);
  font-size: 13px;
  color: var(--color-text);
  background: var(--color-surface);
  outline: none;
}

.add-row input:focus {
  border-color: var(--color-accent);
}

.btn-primary-sm {
  padding: 9px 18px;
  background: var(--color-accent);
  color: white;
  border: none;
  border-radius: var(--radius-pill);
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  flex-shrink: 0;
  transition: background var(--transition-fast);
}

.btn-primary-sm:hover {
  background: var(--color-accent-hover);
}

.cat-list {
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.cat-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  border-bottom: 1px solid var(--color-border-light);
  transition: background var(--transition-fast);
}

.cat-row:last-child {
  border-bottom: none;
}

.cat-row:hover {
  background: var(--color-surface-hover);
}

.cat-name {
  font-size: 13px;
  color: var(--color-text);
}

.inline-edit {
  padding: 4px 10px;
  border: 1.5px solid var(--color-accent);
  border-radius: var(--radius-sm);
  font-family: var(--font-body);
  font-size: 13px;
  color: var(--color-text);
  background: var(--color-surface);
  outline: none;
  width: 160px;
}

.row-actions {
  display: flex;
  gap: 8px;
}

.link-btn {
  border: none;
  background: none;
  font-family: var(--font-body);
  font-size: 12px;
  color: var(--color-accent-text);
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.link-btn:hover {
  opacity: 0.75;
}

.link-btn--danger {
  color: var(--color-danger);
}

.empty {
  padding: 24px;
  text-align: center;
  color: var(--color-text-tertiary);
  font-size: 13px;
}
</style>
