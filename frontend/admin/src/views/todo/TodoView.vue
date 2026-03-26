<template>
  <div class="todo-page">
    <TodoSidebar @open-search="showSearch = true" @open-trash="showTrash = true" />
    <TodoList @create="openCreate" />
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
import TodoDetail from './TodoDetail.vue'
import TodoFormDrawer from './TodoFormDrawer.vue'
import TodoSearchModal from './TodoSearchModal.vue'
import TodoTrashModal from './TodoTrashModal.vue'

const store = useTodoStore()

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
</style>
