<template>
  <div class="news-page">
    <PageHeader title="新闻" back-to="/home">
      <template #right>
        <button class="search-btn" @click="showSearch = !showSearch">
          <svg viewBox="0 0 24 24" fill="none" width="18" height="18">
            <circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="2"/>
            <path d="M21 21l-4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>
      </template>
    </PageHeader>

    <transition name="fade">
      <div v-if="showSearch" class="search-bar">
        <input
          v-model="keyword"
          type="search"
          placeholder="搜索文章..."
          @input="onSearch"
          ref="searchInput"
        />
      </div>
    </transition>

    <div class="cat-strip" v-if="store.categories.length">
      <button
        class="cat-btn"
        :class="{ active: store.filters.category_id === null }"
        @click="store.setFilter('category_id', null)"
      >全部</button>
      <button
        v-for="c in store.categories"
        :key="c.id"
        class="cat-btn"
        :class="{ active: store.filters.category_id === c.id }"
        @click="store.setFilter('category_id', c.id)"
      >{{ c.name }}</button>
    </div>

    <div class="list-area" @scroll="onScroll" ref="listEl">
      <div v-if="store.loading && !store.articles.length" class="list-loading">
        <div class="spinner" />
      </div>
      <div v-else-if="!store.articles.length" class="list-empty">
        <svg viewBox="0 0 48 48" fill="none" width="48" height="48">
          <rect x="8" y="6" width="32" height="36" rx="3" stroke="currentColor" stroke-width="1.5"/>
          <path d="M16 16h16M16 24h12M16 32h8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        <p>暂无文章</p>
      </div>
      <div v-else class="article-list">
        <div
          v-for="a in store.articles"
          :key="a.id"
          class="article-card"
          @click="$router.push('/news/' + a.id)"
        >
          <div class="card-body">
            <div class="card-meta">
              <span v-if="a.category" class="cat-badge">{{ a.category.name }}</span>
              <span class="card-date">{{ formatDate(a.published_at || a.created_at) }}</span>
            </div>
            <h3 class="card-title">{{ a.title }}</h3>
            <p v-if="a.summary" class="card-summary">{{ a.summary }}</p>
            <div class="card-footer" v-if="a.source || a.author">
              <span class="card-source">{{ a.source?.name || a.author }}</span>
            </div>
          </div>
        </div>

        <div v-if="store.loading" class="load-more-spinner">
          <div class="spinner" />
        </div>
        <div v-else-if="store.articles.length >= store.total" class="list-end">— 已加载全部 —</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useNewsStore } from '@/stores/news'
import PageHeader from '@/components/PageHeader.vue'

const store = useNewsStore()
const showSearch = ref(false)
const keyword = ref('')
const listEl = ref(null)
const searchInput = ref(null)

let searchTimer = null
function onSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => store.setFilter('keyword', keyword.value), 400)
}

async function toggleSearch() {
  showSearch.value = !showSearch.value
  if (showSearch.value) {
    await nextTick()
    searchInput.value?.focus()
  } else {
    keyword.value = ''
    store.setFilter('keyword', '')
  }
}

function onScroll(e) {
  const el = e.target
  if (el.scrollHeight - el.scrollTop - el.clientHeight < 100) {
    if (!store.loading && store.articles.length < store.total) {
      store.filters.page++
      store.fetchArticles()
    }
  }
}

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

onMounted(() => {
  store.fetchCategories()
  store.fetchArticles(true)
})
</script>

<style scoped>
.news-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--color-bg);
}

.search-btn {
  width: 36px; height: 36px;
  border: none; background: none;
  color: var(--color-text-secondary);
  display: flex; align-items: center; justify-content: center;
}

.search-bar {
  padding: 8px 16px;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border-light);
  flex-shrink: 0;
}

.search-bar input {
  width: 100%;
  height: 38px;
  padding: 0 14px;
  background: var(--color-bg);
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-full);
  font-size: 14px;
  color: var(--color-text);
  outline: none;
}

.cat-strip {
  display: flex;
  gap: 6px;
  padding: 10px 16px;
  overflow-x: auto;
  flex-shrink: 0;
  scrollbar-width: none;
}

.cat-btn {
  padding: 6px 14px;
  border: none;
  background: none;
  font-size: 13px;
  color: var(--color-text-tertiary);
  border-radius: var(--radius-full);
  white-space: nowrap;
  font-weight: 500;
  transition: all var(--transition-fast);
  flex-shrink: 0;
}
.cat-btn.active {
  background: var(--color-accent-subtle);
  color: var(--color-accent-text);
  font-weight: 600;
}

.list-area {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 24px;
}

.list-loading, .list-empty {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; padding: 64px 24px; gap: 12px;
  color: var(--color-text-tertiary); font-size: 14px;
}

.spinner {
  width: 28px; height: 28px;
  border: 2.5px solid var(--color-border);
  border-top-color: var(--color-accent);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.article-list { padding: 8px 0; }

.article-card {
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border-light);
  transition: background var(--transition-fast);
}
.article-card:active { background: var(--color-border-light); }

.card-body { padding: 16px; }

.card-meta {
  display: flex; align-items: center; gap: 8px; margin-bottom: 8px;
}

.cat-badge {
  font-size: 11px; font-weight: 500;
  padding: 2px 8px;
  background: var(--color-accent-subtle);
  color: var(--color-accent-text);
  border-radius: var(--radius-full);
}

.card-date { font-size: 12px; color: var(--color-text-tertiary); }

.card-title {
  font-size: 16px; font-weight: 600;
  color: var(--color-text);
  line-height: 1.4;
  margin-bottom: 6px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-summary {
  font-size: 13px; color: var(--color-text-secondary);
  line-height: 1.5; margin-bottom: 10px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer { }
.card-source { font-size: 12px; color: var(--color-text-tertiary); }

.load-more-spinner {
  display: flex; justify-content: center; padding: 20px;
}

.list-end {
  text-align: center; font-size: 12px;
  color: var(--color-text-tertiary); padding: 20px;
}
</style>
