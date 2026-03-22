import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as api from '@/api/todo'

export const useTodoStore = defineStore('todo', () => {
  const items = ref([])
  const total = ref(0)
  const categories = ref([])
  const tags = ref([])
  const filters = ref({ status: null, priority: null, category_id: null, page: 1, page_size: 50 })
  const loading = ref(false)

  async function fetchCategories() {
    const { data } = await api.getCategories()
    categories.value = data
  }

  async function fetchTags() {
    const { data } = await api.getTags()
    tags.value = data
  }

  async function fetchItems() {
    loading.value = true
    try {
      const params = {}
      for (const [k, v] of Object.entries(filters.value)) {
        if (v !== null && v !== undefined) params[k] = v
      }
      const { data } = await api.getItems(params)
      items.value = data.items
      total.value = data.total
    } finally {
      loading.value = false
    }
  }

  function setFilter(key, value) {
    filters.value[key] = value
    filters.value.page = 1
    fetchItems()
  }

  function resetFilters() {
    filters.value = { status: null, priority: null, category_id: null, page: 1, page_size: 50 }
    fetchItems()
  }

  return { items, total, categories, tags, filters, loading, fetchCategories, fetchTags, fetchItems, setFilter, resetFilters }
})
