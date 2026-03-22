import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as api from '@/api/news'

export const useNewsStore = defineStore('news', () => {
  const articles = ref([])
  const total = ref(0)
  const categories = ref([])
  const filters = ref({ keyword: '', category_id: null, page: 1, page_size: 20 })
  const loading = ref(false)

  async function fetchCategories() {
    const { data } = await api.getCategories()
    categories.value = data
  }

  async function fetchArticles(reset = false) {
    if (reset) {
      filters.value.page = 1
      articles.value = []
    }
    loading.value = true
    try {
      const params = {}
      for (const [k, v] of Object.entries(filters.value)) {
        if (v !== null && v !== '' && v !== undefined) params[k] = v
      }
      const { data } = await api.getArticles(params)
      if (reset || filters.value.page === 1) {
        articles.value = data.items
      } else {
        articles.value.push(...data.items)
      }
      total.value = data.total
    } finally {
      loading.value = false
    }
  }

  function setFilter(key, value) {
    filters.value[key] = value
    fetchArticles(true)
  }

  return { articles, total, categories, filters, loading, fetchCategories, fetchArticles, setFilter }
})
