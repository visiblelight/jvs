import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const saved = localStorage.getItem('theme')
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  const theme = ref(saved || (prefersDark ? 'dark' : 'light'))

  function applyTheme(t) {
    document.documentElement.setAttribute('data-theme', t)
  }

  function toggle() {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
  }

  watch(theme, (val) => {
    localStorage.setItem('theme', val)
    applyTheme(val)
  }, { immediate: true })

  return { theme, toggle }
})
