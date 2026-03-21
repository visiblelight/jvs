<template>
  <Teleport to="body">
    <div class="overlay" @click.self="$emit('close')">
      <div class="modal" @click.stop>
        <div class="modal-head">
          <h3>标签管理</h3>
          <button class="close-btn" @click="$emit('close')">
            <svg viewBox="0 0 16 16" fill="currentColor" width="16" height="16"><path d="M3.72 3.72a.75.75 0 011.06 0L8 6.94l3.22-3.22a.75.75 0 111.06 1.06L9.06 8l3.22 3.22a.75.75 0 11-1.06 1.06L8 9.06l-3.22 3.22a.75.75 0 01-1.06-1.06L6.94 8 3.72 4.78a.75.75 0 010-1.06z"/></svg>
          </button>
        </div>

        <div class="modal-body">
          <div class="add-row">
            <input v-model="newName" placeholder="新标签名称" @keyup.enter="handleAdd" />
            <input v-model="newColor" type="color" class="color-picker" />
            <button class="btn-primary-sm" @click="handleAdd">添加</button>
          </div>

          <div class="tag-list">
            <div v-for="tag in store.tags" :key="tag.id" class="tag-row">
              <template v-if="editingId !== tag.id">
                <span class="tag-dot" :style="{ background: tag.color }"></span>
                <span class="tag-name">{{ tag.name }}</span>
              </template>
              <template v-else>
                <input v-model="editingColor" type="color" class="color-picker" />
                <input v-model="editingName" class="inline-edit" @keyup.enter="saveEdit(tag.id)" />
              </template>
              <div class="row-actions">
                <button v-if="editingId !== tag.id" class="link-btn" @click="startEdit(tag)">编辑</button>
                <button v-else class="link-btn" @click="saveEdit(tag.id)">保存</button>
                <button class="link-btn link-btn--danger" @click="handleDelete(tag.id)">删除</button>
              </div>
            </div>
            <div v-if="store.tags.length === 0" class="empty">暂无标签</div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'
import { useTodoStore } from '@/stores/todo'
import { createTag, updateTag, deleteTag } from '@/api/todo'

const emit = defineEmits(['close'])
const store = useTodoStore()

const newName = ref('')
const newColor = ref('#0d9488')
const editingId = ref(null)
const editingName = ref('')
const editingColor = ref('#0d9488')

async function handleAdd() {
  if (!newName.value.trim()) return
  await createTag({ name: newName.value.trim(), color: newColor.value })
  newName.value = ''
  newColor.value = '#0d9488'
  await store.fetchTags()
}

function startEdit(tag) {
  editingId.value = tag.id
  editingName.value = tag.name
  editingColor.value = tag.color
}

async function saveEdit(id) {
  if (!editingName.value.trim()) return
  await updateTag(id, { name: editingName.value.trim(), color: editingColor.value })
  editingId.value = null
  await store.fetchTags()
}

async function handleDelete(id) {
  if (!confirm('确定删除？')) return
  await deleteTag(id)
  await store.fetchTags()
}
</script>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(4px);
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
  border-radius: var(--radius-lg);
  width: 440px;
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
  padding: 8px 12px;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-family: var(--font-body);
  font-size: 13px;
  color: var(--color-text);
  background: var(--color-surface);
  outline: none;
}

.add-row input:focus {
  border-color: var(--color-accent);
}

.color-picker {
  width: 38px !important;
  height: 38px;
  flex: none !important;
  padding: 3px !important;
  border: 1.5px solid var(--color-border) !important;
  border-radius: var(--radius-sm) !important;
  cursor: pointer;
  background: var(--color-surface) !important;
}

.btn-primary-sm {
  padding: 8px 16px;
  background: var(--color-accent);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
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

.tag-list {
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.tag-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  border-bottom: 1px solid var(--color-border-light);
  transition: background var(--transition-fast);
}

.tag-row:last-child {
  border-bottom: none;
}

.tag-row:hover {
  background: var(--color-surface-hover);
}

.tag-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.tag-name {
  flex: 1;
  font-size: 13px;
  color: var(--color-text);
}

.inline-edit {
  flex: 1;
  padding: 4px 10px;
  border: 1.5px solid var(--color-accent);
  border-radius: var(--radius-sm);
  font-family: var(--font-body);
  font-size: 13px;
  color: var(--color-text);
  background: var(--color-surface);
  outline: none;
}

.row-actions {
  display: flex;
  gap: 8px;
  margin-left: auto;
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
