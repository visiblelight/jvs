<template>
  <div class="todo-page">
    <TodoSidebar
      @manage-categories="showCategoryManager = true"
      @manage-tags="showTagManager = true"
    />
    <TodoList @create="openCreate" />
    <TodoDetail @edit="openEdit" />

    <TodoFormModal
      v-if="showForm"
      :edit-item="editItem"
      @close="showForm = false"
      @saved="onSaved"
    />
    <CategoryManager v-if="showCategoryManager" @close="showCategoryManager = false" />
    <TagManager v-if="showTagManager" @close="showTagManager = false" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useTodoStore } from '@/stores/todo'
import TodoSidebar from './TodoSidebar.vue'
import TodoList from './TodoList.vue'
import TodoDetail from './TodoDetail.vue'
import TodoFormModal from './TodoFormModal.vue'
import CategoryManager from './CategoryManager.vue'
import TagManager from './TagManager.vue'

const store = useTodoStore()

const showForm = ref(false)
const editItem = ref(null)
const showCategoryManager = ref(false)
const showTagManager = ref(false)

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
