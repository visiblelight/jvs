<template>
  <div class="todo-page">
    <TodoSidebar @open-search="showSearch = true" @open-trash="showTrash = true" />
    <div class="center-area">
      <div class="view-toggle-bar">
        <div class="segmented-control">
          <button class="segment-btn active-scale" :class="{ active: viewMode === 'list' }" @click="viewMode = 'list'">
            <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14"><path d="M2 4a1 1 0 011-1h10a1 1 0 110 2H3a1 1 0 01-1-1zm0 4a1 1 0 011-1h10a1 1 0 110 2H3a1 1 0 01-1-1zm1 3a1 1 0 100 2h10a1 1 0 100-2H3z"/></svg>
            列表
          </button>
          <button class="segment-btn active-scale" :class="{ active: viewMode === 'calendar' }" @click="viewMode = 'calendar'">
            <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14"><path d="M4.5 1a.5.5 0 01.5.5V2h6v-.5a.5.5 0 011 0V2h1a2 2 0 012 2v8a2 2 0 01-2 2H3a2 2 0 01-2-2V4a2 2 0 012-2h1v-.5a.5.5 0 01.5-.5zM3 6v6a1 1 0 001 1h8a1 1 0 001-1V6H3z"/></svg>
            日历
          </button>
        </div>
        <button class="btn-create active-scale" @click="openCreate">
          <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14"><path d="M8 2a.75.75 0 01.75.75v4.5h4.5a.75.75 0 010 1.5h-4.5v4.5a.75.75 0 01-1.5 0v-4.5h-4.5a.75.75 0 010-1.5h4.5v-4.5A.75.75 0 018 2z"/></svg>
          新建
        </button>
      </div>
      <TodoList v-if="viewMode === 'list'" @create="openCreate" />
      <TodoCalendarView v-else />
    </div>
    <TodoDetail @edit="openEdit" />

    <TodoFormDrawer
      v-if="showForm"
      :edit-item="editItem"
      @close="showForm = false"
      @saved="onSaved"
    />
    
    <TodoSearchModal 
      v-model:visible="showSearch" 
      @select="onSearchSelect" 
    />
    <TodoTrashModal v-model:visible="showTrash" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useTodoStore } from '@/stores/todo'
import TodoSidebar from './TodoSidebar.vue'
import TodoList from './TodoList.vue'
import TodoCalendarView from './TodoCalendarView.vue'
import TodoDetail from './TodoDetail.vue'
import TodoFormDrawer from './TodoFormDrawer.vue'
import TodoSearchModal from './TodoSearchModal.vue'
import TodoTrashModal from './TodoTrashModal.vue'

const store = useTodoStore()

const viewMode = ref('list')
const showForm = ref(false)
const showSearch = ref(false)
const showTrash = ref(false)
const editItem = ref(null)

function openCreate() {
  editItem.value = null
  showForm.value = true
}

function openEdit(item) {
  editItem.value = item
  showForm.value = true
}

function onSaved() {
  showForm.value = false
  store.fetchItems()
  if (editItem.value) {
    store.selectItem(editItem.value.id)
  }
}

function onSearchSelect(item) {
  store.selectItem(item.id)
}

function handleKeydown(e) {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault()
    showSearch.value = true
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
  store.fetchCategories()
  store.fetchTags()
  store.fetchItems()
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.todo-page {
  display: flex;
  height: 100vh;
}

.center-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  border-right: 1px solid var(--color-border-light);
}

.view-toggle-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 20px;
  border-bottom: 1px solid var(--color-border-light);
  flex-shrink: 0;
  background: var(--color-surface);
}

.view-toggle-bar .segmented-control {
  gap: 2px;
}

.view-toggle-bar .segment-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  padding: 6px 12px;
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
</style>
