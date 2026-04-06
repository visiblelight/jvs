import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as api from '@/api/tick'

export const useTickStore = defineStore('tick', () => {
  const tasks = ref([])
  const total = ref(0)
  const loading = ref(false)

  async function fetchTasks() {
    loading.value = true
    try {
      const { data } = await api.getTasks({ is_archived: false })
      tasks.value = data.items
      total.value = data.total
    } finally {
      loading.value = false
    }
  }

  return { tasks, total, loading, fetchTasks }
})
