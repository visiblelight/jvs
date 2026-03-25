<template>
  <div class="todo-sidebar">
    <!-- Status -->
    <div class="section">
      <div class="section-head">
        <h3 class="section-label">状态</h3>
      </div>
      <div class="filter-group">
        <button
          v-for="s in statusOptions"
          :key="s.value"
          class="filter-chip active-scale"
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
        <button class="section-btn active-scale" @click="toggleAddCat(null)">
          <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14" v-if="showAddCat === null"><path d="M2 8a.75.75 0 01.75-.75h10.5a.75.75 0 010 1.5H2.75A.75.75 0 012 8z"/></svg>
          <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14" v-else><path d="M8 2a.75.75 0 01.75.75v4.5h4.5a.75.75 0 010 1.5h-4.5v4.5a.75.75 0 01-1.5 0v-4.5h-4.5a.75.75 0 010-1.5h4.5v-4.5A.75.75 0 018 2z"/></svg>
        </button>
      </div>

      <div class="tree-list">
        <button
          class="tree-item active-scale"
          :class="{ active: store.filters.category_id === null }"
          @click="store.setFilter('category_id', null)"
          style="padding-left: 12px; margin-bottom: 4px;"
        >
          全部事项
        </button>

        <div v-if="showAddCat === null" class="inline-add" style="padding-left:12px; margin-bottom:8px">
          <input 
            v-model="newCatName" 
            placeholder="新主分类回车..." 
            @keyup.enter="handleAddCat(null, newCatName)" 
            @keyup.esc="showAddCat = false" 
            class="inline-input" 
            autofocus 
          />
          <button class="inline-cancel" @click="showAddCat = false" title="取消">×</button>
        </div>

        <TodoCategoryTree 
          :categories="store.categories" 
          :selected-id="store.filters.category_id"
          :add-parent-id="showAddCat"
          @select="id => store.setFilter('category_id', id)"
          @add="id => toggleAddCat(id)"
          @delete="cat => confirmDeleteCategory(cat)"
          @submit-add="payload => handleAddCat(payload.parentId, payload.name)"
          @cancel-add="showAddCat = false"
        />
      </div>
    </div>

    <!-- Tags -->
    <div class="section">
      <div class="section-head">
        <h3 class="section-label">标签</h3>
        <button class="section-btn active-scale" @click="showAddTag = !showAddTag">
          <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14" v-if="showAddTag"><path d="M2 8a.75.75 0 01.75-.75h10.5a.75.75 0 010 1.5H2.75A.75.75 0 012 8z"/></svg>
          <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14" v-else><path d="M8 2a.75.75 0 01.75.75v4.5h4.5a.75.75 0 010 1.5h-4.5v4.5a.75.75 0 01-1.5 0v-4.5h-4.5a.75.75 0 010-1.5h4.5v-4.5A.75.75 0 018 2z"/></svg>
        </button>
      </div>
      <div class="tree-list">
        <button
          class="tree-item active-scale"
          :class="{ active: store.filters.tag_id === null }"
          @click="store.setFilter('tag_id', null)"
          style="padding-left: 12px; padding-right: 12px; margin-bottom: 4px;"
        >所有标签</button>

        <div v-if="showAddTag" class="inline-add" style="padding-left:12px; margin-bottom:8px">
          <input 
            v-model="newTagName" 
            placeholder="新标签回车..." 
            @keyup.enter="handleAddTag" 
            @keyup.esc="showAddTag = false" 
            class="inline-input" 
            autofocus 
          />
          <button class="inline-cancel" @click="showAddTag = false" title="取消">×</button>
        </div>

        <button
          v-for="tag in store.tags"
          :key="tag.id"
          class="tree-item active-scale tag-item"
          :class="{ active: store.filters.tag_id === tag.id }"
          @click="store.setFilter('tag_id', store.filters.tag_id === tag.id ? null : tag.id)"
          style="padding-left: 12px; padding-right: 12px;"
        >
          <span class="chip-dot" :style="{ background: tag.color }"></span>
          <span class="item-name">{{ tag.name }}</span>
          <span class="tree-actions">
            <span class="action-icon del" @click.stop="confirmDeleteTag(tag)">×</span>
          </span>
        </button>
      </div>
    </div>

    <!-- UI Custom Confirm Modal -->
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
</template>

<script setup>
import { ref } from 'vue'
import { useTodoStore } from '@/stores/todo'
import { createCategory, deleteCategory, createTag, deleteTag } from '@/api/todo'
import TodoCategoryTree from './TodoCategoryTree.vue'

const store = useTodoStore()

const statusOptions = [
  { value: 'pending', label: '未完成', color: 'var(--color-status-pending)' },
  { value: 'paused', label: '暂停中', color: 'var(--color-status-paused)' },
  { value: 'completed', label: '已完成', color: 'var(--color-status-completed)' },
]

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


// --- Category Inline Management ---
// showAddCat holds parent_id. false: none, null: top-level, id: secondary level
const showAddCat = ref(false)
const newCatName = ref('')

function toggleAddCat(parentId) {
  if (showAddCat.value === parentId) {
    showAddCat.value = false
  } else {
    showAddCat.value = parentId
    newCatName.value = ''
  }
}

async function handleAddCat(parentId, newName) {
  const name = newName.trim()
  if (!name) return
  await createCategory({ name, parent_id: parentId })
  if (parentId === null) {
    newCatName.value = ''
  }
  showAddCat.value = false
  await store.fetchCategories()
}

function confirmDeleteCategory(cat) {
  customConfirm(`确认删除分类「${cat.name}」吗？关联事项不会被删除，但将失去该分类标签。`, async () => {
    await deleteCategory(cat.id)
    await store.fetchCategories()
    store.fetchItems()
  })
}

// --- Tag Inline Management ---
const showAddTag = ref(false)
const newTagName = ref('')

async function handleAddTag() {
  const name = newTagName.value.trim()
  if (!name) return
  const color = '#' + Math.floor(Math.random()*16777215).toString(16).padEnd(6, '0')
  await createTag({ name, color })
  newTagName.value = ''
  showAddTag.value = false
  await store.fetchTags()
}

function confirmDeleteTag(tag) {
  customConfirm(`确认删除标签「${tag.name}」吗？关联事项将不再拥有该标签。`, async () => {
    await deleteTag(tag.id)
    await store.fetchTags()
    store.fetchItems()
  })
}
</script>

<style scoped>
.todo-sidebar {
  width: 250px;
  background: var(--color-surface);
  border-right: 1px solid var(--color-border-light);
  overflow-y: auto;
  padding: 0;
  flex-shrink: 0;
}

.section {
  padding: 24px 0;
  border-bottom: 1px solid var(--color-border-light);
}
.section:last-child {
  border-bottom: none;
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px 0 20px;
  margin-bottom: 8px;
}

.section-label {
  font-family: var(--font-body);
  font-size: 11px;
  font-weight: 700;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.8px;
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
  color: var(--color-text);
  transform: scale(0.96);
}

.filter-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 0 20px;
}

.filter-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-pill);
  background: var(--color-surface);
  font-family: var(--font-body);
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.filter-chip:hover {
  border-color: var(--color-text-tertiary);
  box-shadow: var(--shadow-sm);
}

.filter-chip.active {
  background: var(--color-accent-subtle);
  border-color: transparent;
  color: var(--color-accent-text);
  box-shadow: none;
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
  gap: 2px;
  padding: 0 8px;
}

.tree-item {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding-top: 8px;
  padding-bottom: 8px;
  border: none;
  border-radius: var(--radius-sm);
  background: transparent;
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary);
  cursor: pointer;
  text-align: left;
  transition: all var(--transition-fast);
}

.tag-item .item-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tree-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
}
.action-icon {
  color: var(--color-text-tertiary);
  font-size: 16px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 4px;
}
.action-icon:hover {
  color: var(--color-text);
  background: var(--color-surface-hover);
}
.action-icon.del:hover {
  color: var(--color-danger);
  background: var(--color-danger-subtle, rgba(239, 68, 68, 0.15));
}

.tree-item:hover {
  background: var(--color-surface-hover);
  color: var(--color-text);
}
.tree-item:hover .tree-actions {
  opacity: 1;
}

.tree-item.active {
  background: var(--color-accent-subtle);
  color: var(--color-accent-text);
}

.inline-add {
  display: flex;
  align-items: center;
  gap: 6px;
  animation: fadeIn 0.2s;
}

.inline-input {
  flex: 1;
  width: 100%;
  padding: 8px 10px;
  border: 1px solid var(--color-accent);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  color: var(--color-text);
  font-size: 12px;
  outline: none;
  box-shadow: 0 0 0 3px var(--color-accent-subtle);
}

.inline-cancel {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: var(--radius-sm);
  background: var(--color-bg-base);
  color: var(--color-text-secondary);
  cursor: pointer;
}
.inline-cancel:hover {
  background: var(--color-surface-hover);
  color: var(--color-text);
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

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
