<template>
  <div class="todo-page">
    <TodoSidebar />
    <TodoList @create="openCreate" />
    <TodoDetail @edit="openEdit" />

    <TodoFormDrawer
      v-if="showForm"
      :edit-item="editItem"
      @close="showForm = false"
      @saved="onSaved"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useTodoStore } from '@/stores/todo'
import TodoSidebar from './TodoSidebar.vue'
import TodoList from './TodoList.vue'
import TodoDetail from './TodoDetail.vue'
import TodoFormDrawer from './TodoFormDrawer.vue'

const store = useTodoStore()

const showForm = ref(false)
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

onMounted(() => {
  store.fetchCategories()
  store.fetchTags()
  store.fetchItems()
})
</script>

<style scoped>
.todo-page {
  display: flex;
  height: 100vh;
}
</style>
