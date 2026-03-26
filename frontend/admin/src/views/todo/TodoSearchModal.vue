<template>
  <Teleport to="body">
    <transition name="modal-fade">
      <div v-if="visible" class="search-overlay" @click.self="close">
        <div class="search-modal" role="dialog" aria-modal="true" @click.stop>
          <div class="search-header">
            <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
            <input 
              ref="searchInput"
              type="text" 
              class="search-input" 
              placeholder="搜索待办事项..." 
              v-model="query"
              @keydown.down.prevent="selectNext"
              @keydown.up.prevent="selectPrev"
              @keydown.enter.prevent="handleEnter"
              @keydown.esc.prevent="close"
            />
            <button class="search-close" @click="close" title="关闭 (Esc)">
              <span class="esc-badge">ESC</span>
            </button>
          </div>

          <div class="search-body">
            <div v-if="loading" class="search-state">
              <span class="loader"></span>
              <p>正在搜索...</p>
            </div>
            
            <div v-else-if="results.length === 0 && query.trim() !== ''" class="search-state">
              <svg viewBox="0 0 24 24" width="32" height="32" stroke="currentColor" stroke-width="1.5" fill="none"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
              <p>没有找到与 "{{ query }}" 相关的事项</p>
            </div>
            
            <div v-else-if="results.length > 0" class="search-results">
              <ul class="result-list">
                <li 
                  v-for="(item, index) in results" 
                  :key="item.id"
                  class="result-item"
                  :class="{ active: activeIndex === index }"
                  @mouseenter="activeIndex = index"
                  @click="handleSelect(item)"
                >
                  <span 
                    class="status-dot" 
                    :class="{ 
                      'status-dot--pending': item.status === 'pending',
                      'status-dot--paused': item.status === 'paused',
                      'status-dot--completed': item.status === 'completed'
                    }"
                  ></span>
                  
                  <div class="result-info">
                    <h4 class="result-title" v-html="highlight(item.title)"></h4>
                    <p class="result-desc" v-if="item.description" v-html="highlight(item.description)"></p>
                    
                    <div class="result-meta">
                      <span class="meta-badge priority" :class="'p-' + item.priority">P{{ item.priority }}</span>
                      <span class="meta-date" v-if="item.due_date">{{ formatDate(item.due_date) }}</span>
                    </div>
                  </div>
                </li>
              </ul>
            </div>

            <div v-else class="search-state">
              <p class="hint-text">输入关键字开始全局搜索</p>
            </div>
          </div>
          
          <div class="search-footer">
            <div class="footer-hint">
              <kbd>↑</kbd> <kbd>↓</kbd> <span>导航</span>
            </div>
            <div class="footer-hint">
              <kbd>↵</kbd> <span>确认</span>
            </div>
            <div class="footer-hint">
              <kbd>Esc</kbd> <span>关闭</span>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script setup>
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { getItems } from '@/api/todo'
import { useTodoStore } from '@/stores/todo'

const props = defineProps({
  visible: { type: Boolean, default: false }
})

const emit = defineEmits(['update:visible', 'select'])
const store = useTodoStore()

const searchInput = ref(null)
const query = ref('')
const results = ref([])
const loading = ref(false)
const activeIndex = ref(-1)

let debounceTimer = null

watch(() => props.visible, async (val) => {
  if (val) {
    query.value = ''
    results.value = []
    activeIndex.value = -1
    await nextTick()
    searchInput.value?.focus()
  }
})

watch(query, (newVal) => {
  if (debounceTimer) clearTimeout(debounceTimer)
  
  if (!newVal.trim()) {
    results.value = []
    loading.value = false
    return
  }

  loading.value = true
  debounceTimer = setTimeout(async () => {
    try {
      const response = await getItems({
        q: newVal.trim(),
        page: 1,
        page_size: 50
      })
      results.value = response.data.items || []
      activeIndex.value = results.value.length > 0 ? 0 : -1
    } catch (e) {
      console.error(e)
    } finally {
      loading.value = false
    }
  }, 300)
})

function close() {
  emit('update:visible', false)
}

function selectNext() {
  if (results.value.length === 0) return
  activeIndex.value = (activeIndex.value + 1) % results.value.length
  scrollToActive()
}

function selectPrev() {
  if (results.value.length === 0) return
  activeIndex.value = (activeIndex.value - 1 + results.value.length) % results.value.length
  scrollToActive()
}

function scrollToActive() {
  nextTick(() => {
    const activeEl = document.querySelector('.result-item.active')
    if (activeEl) {
      activeEl.scrollIntoView({ block: 'nearest' })
    }
  })
}

function handleEnter() {
  if (activeIndex.value >= 0 && activeIndex.value < results.value.length) {
    handleSelect(results.value[activeIndex.value])
  } else if (results.value.length === 1) {
    handleSelect(results.value[0])
  }
}

function handleSelect(item) {
  emit('select', item)
  close()
}

function highlight(text) {
  if (!text || !query.value) return text
  const safeQuery = query.value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const regex = new RegExp(`(${safeQuery})`, 'gi')
  return text.replace(regex, '<mark>$1</mark>')
}

function formatDate(d) {
  if (!d) return ''
  const date = new Date(d)
  return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
}
</script>

<style scoped>
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.search-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  z-index: 9999;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding-top: 12vh;
}

.search-modal {
  width: 100%;
  max-width: 600px;
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid var(--color-border);
  animation: modal-slide-down 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes modal-slide-down {
  from { opacity: 0; transform: translateY(-20px) scale(0.98); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.search-header {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--color-border-light);
  gap: 12px;
}

.search-icon {
  width: 20px;
  height: 20px;
  color: var(--color-accent);
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  font-family: var(--font-body);
  font-size: 18px;
  color: var(--color-text);
  outline: none;
}
.search-input::placeholder {
  color: var(--color-text-tertiary);
}

.search-close {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
}

.esc-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 4px;
  background: var(--color-bg-base);
  color: var(--color-text-tertiary);
  border: 1px solid var(--color-border);
}

.search-body {
  max-height: 45vh;
  overflow-y: auto;
  min-height: 100px;
  display: flex;
  flex-direction: column;
}

.search-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: var(--color-text-tertiary);
  gap: 12px;
}

.hint-text {
  font-size: 14px;
}

.loader {
  width: 24px;
  height: 24px;
  border: 3px solid var(--color-border);
  border-bottom-color: var(--color-accent);
  border-radius: 50%;
  animation: rotation 1s linear infinite;
}

@keyframes rotation {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.search-results {
  padding: 8px;
}

.result-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.result-item {
  display: flex;
  align-items: flex-start;
  padding: 12px 16px;
  gap: 14px;
  border-radius: var(--radius-md);
  cursor: pointer;
  background: transparent;
  transition: all 0.1s ease;
}

.result-item.active {
  background: var(--color-accent-subtle);
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-top: 6px;
  flex-shrink: 0;
}
.status-dot--pending { background: var(--color-status-pending); }
.status-dot--paused { background: var(--color-status-paused); }
.status-dot--completed { background: var(--color-status-completed); }

.result-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.result-title {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.result-desc {
  margin: 0;
  font-size: 12px;
  color: var(--color-text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

:deep(mark) {
  background: color-mix(in srgb, var(--color-accent) 25%, transparent);
  color: var(--color-text);
  border-radius: 2px;
  padding: 0 2px;
}

.result-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 4px;
}

.meta-badge {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 600;
}
.meta-badge.p-1, .meta-badge.p-2 { background: var(--color-surface-hover); color: var(--color-text-secondary); }
.meta-badge.p-3 { background: var(--color-info-subtle, #e0f2fe); color: var(--color-info, #0284c7); }
.meta-badge.p-4, .meta-badge.p-5 { background: rgba(217, 119, 6, 0.1); color: var(--color-warning); }

.meta-date {
  font-size: 11px;
  color: var(--color-text-tertiary);
}

.search-footer {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 20px;
  border-top: 1px solid var(--color-border-light);
  background: var(--color-bg-base);
}

.footer-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--color-text-secondary);
}

kbd {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 4px;
  font-family: inherit;
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text-tertiary);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  box-shadow: 0 1px 1px rgba(0,0,0,0.05);
}
</style>
