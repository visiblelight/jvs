<template>
  <div class="news-page">
    <NewsList @create="openCreate" @edit="openEdit" />
    <NewsDetail @edit="openEdit" />

    <NewsFormDrawer
      v-if="showForm"
      :edit-article="editArticle"
      @close="showForm = false"
      @saved="onSaved"
    />
    <NewsCategoryManager v-if="showCategoryManager" @close="showCategoryManager = false" />
    <NewsSourceManager v-if="showSourceManager" @close="showSourceManager = false" />
  </div>
</template>

<script setup>
import { ref, onMounted, provide } from 'vue'
import { useNewsStore } from '@/stores/news'
import NewsList from './NewsList.vue'
import NewsDetail from './NewsDetail.vue'
import NewsFormDrawer from './NewsFormDrawer.vue'
import NewsCategoryManager from './NewsCategoryManager.vue'
import NewsSourceManager from './NewsSourceManager.vue'

const store = useNewsStore()

const showForm = ref(false)
const editArticle = ref(null)
const showCategoryManager = ref(false)
const showSourceManager = ref(false)

provide('showCategoryManager', showCategoryManager)
provide('showSourceManager', showSourceManager)

function openCreate() {
  editArticle.value = null
  showForm.value = true
}

function openEdit(article) {
  editArticle.value = article
  showForm.value = true
}

function onSaved() {
  showForm.value = false
  store.fetchArticles()
  if (editArticle.value) {
    store.selectArticle(editArticle.value.id)
  }
}

onMounted(() => {
  store.fetchCategories()
  store.fetchSources()
  store.fetchArticles()
})
</script>

<style scoped>
.news-page {
  display: flex;
  height: 100vh;
}
</style>
