import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as todoApi from '@/api/todo'

export const useTodoStore = defineStore('todo', () => {
  const categories = ref([])
  const tags = ref([])
  const items = ref([])
  const total = ref(0)
  const currentItem = ref(null)
  const calendarItems = ref([])
  const calendarRange = ref({ start: null, end: null })
  const filters = ref({
    status: null,
    category_id: null,
    tag_id: null,
    priority: null,
    importance: null,
    is_deleted: false,
    page: 1,
    page_size: 50,
  })

  async function fetchCategories() {
    const { data } = await todoApi.getCategories()
    categories.value = data
  }

  async function fetchTags() {
    const { data } = await todoApi.getTags()
    tags.value = data
  }

  async function fetchItems() {
    const params = {}
    for (const [k, v] of Object.entries(filters.value)) {
      if (v !== null && v !== undefined) params[k] = v
    }
    const { data } = await todoApi.getItems(params)
    items.value = data.items
    total.value = data.total
  }

  async function selectItem(id) {
    if (!id) {
      currentItem.value = null
      return
    }
    const { data } = await todoApi.getItem(id)
    currentItem.value = data
  }

  function setFilter(key, value) {
    filters.value[key] = value
    filters.value.page = 1
    fetchItems()
  }

  function resetFilters() {
    filters.value = { status: null, category_id: null, tag_id: null, priority: null, importance: null, is_deleted: false, page: 1, page_size: 50 }
    fetchItems()
  }

  async function fetchCalendarItems(start, end) {
    calendarRange.value = { start, end }
    const { data } = await todoApi.getCalendarItems({
      start: start.toISOString(),
      end: end.toISOString(),
    })
    calendarItems.value = data.items
  }

  return {
    categories, tags, items, total, currentItem, filters,
    calendarItems, calendarRange,
    fetchCategories, fetchTags, fetchItems, selectItem,
    setFilter, resetFilters, fetchCalendarItems,
  }
})
