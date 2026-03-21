import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as api from '@/api/news'

export const useNewsStore = defineStore('news', () => {
  // 分类
  const categories = ref([])
  async function fetchCategories() {
    const { data } = await api.getCategories()
    categories.value = data
  }

  // 来源
  const sources = ref([])
  async function fetchSources() {
    const { data } = await api.getSources()
    sources.value = data
  }

  // 文章
  const articles = ref([])
  const total = ref(0)
  const selectedArticle = ref(null)
  const filters = ref({
    category_id: null,
    source_id: null,
    keyword: '',
    page: 1,
    page_size: 20,
  })

  async function fetchArticles() {
    const params = {}
    if (filters.value.category_id) params.category_id = filters.value.category_id
    if (filters.value.source_id) params.source_id = filters.value.source_id
    if (filters.value.keyword) params.keyword = filters.value.keyword
    params.page = filters.value.page
    params.page_size = filters.value.page_size

    const { data } = await api.getArticles(params)
    articles.value = data.items
    total.value = data.total
  }

  async function selectArticle(id) {
    if (!id) {
      selectedArticle.value = null
      return
    }
    const { data } = await api.getArticle(id)
    selectedArticle.value = data
  }

  function setFilter(key, value) {
    filters.value[key] = value
    filters.value.page = 1
    fetchArticles()
  }

  function setPage(page) {
    filters.value.page = page
    fetchArticles()
  }

  return {
    categories, fetchCategories,
    sources, fetchSources,
    articles, total, selectedArticle, filters,
    fetchArticles, selectArticle, setFilter, setPage,
  }
})
