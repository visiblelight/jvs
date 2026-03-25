<template>
  <div class="news-list">
    <div class="list-header">
      <div class="header-info">
        <h2 class="list-title">文章</h2>
        <span class="list-count">{{ store.total }}</span>
      </div>
      <div class="header-actions">
        <button class="btn-icon" title="分类管理" @click="showCategoryManager = true">
          <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14"><path d="M1 3.5A1.5 1.5 0 012.5 2h3.879a1.5 1.5 0 011.06.44l1.122 1.12A1.5 1.5 0 009.62 4H13.5A1.5 1.5 0 0115 5.5v7a1.5 1.5 0 01-1.5 1.5h-11A1.5 1.5 0 011 12.5v-9z"/></svg>
        </button>
        <button class="btn-icon" title="来源管理" @click="showSourceManager = true">
          <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14"><path d="M8 0a8 8 0 100 16A8 8 0 008 0zM6.5 1.768a6.5 6.5 0 00-4.252 4.482H4.5a10.74 10.74 0 012-4.482zM1.5 7.75h3.25A12.24 12.24 0 004.5 9.5H1.748A6.47 6.47 0 011.5 7.75zm.248 3.25H4.5a10.74 10.74 0 01-2 4.482A6.5 6.5 0 012.248 11h-.5zM7.25 1.543A9.24 9.24 0 004.957 6.25h2.293V1.543zm0 6.207H4.708c-.08.581-.125 1.168-.133 1.75h2.675V7.75zm0 3.25H4.957A9.24 9.24 0 007.25 15.707V11zm1.5 4.707A9.24 9.24 0 0011.043 11H8.75v4.707zm0-6.207h2.675a10.74 10.74 0 01-.133-1.75H8.75V9.5zm0-3.25h2.293A9.24 9.24 0 008.75 1.543V6.25zm3.75 0h2.252a6.5 6.5 0 00-4.252-4.482 10.74 10.74 0 012 4.482zm2.5 1.5h-3.25c.051.581.079 1.168.083 1.75h3.167a6.47 6.47 0 01-.25 1.75H11.5a10.74 10.74 0 01-2 4.482 6.5 6.5 0 004.252-4.482H11.5a12.24 12.24 0 00.25-3.5z"/></svg>
        </button>
        <button class="btn-create" @click="$emit('create')">
          <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14"><path d="M8 2a.75.75 0 01.75.75v4.5h4.5a.75.75 0 010 1.5h-4.5v4.5a.75.75 0 01-1.5 0v-4.5h-4.5a.75.75 0 010-1.5h4.5v-4.5A.75.75 0 018 2z"/></svg>
          新建
        </button>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <input
        class="search-input"
        type="text"
        placeholder="搜索文章..."
        :value="store.filters.keyword"
        @input="debounceSearch($event.target.value)"
      />
      <select class="filter-select" :value="store.filters.category_id || ''" @change="store.setFilter('category_id', $event.target.value ? Number($event.target.value) : null)">
        <option value="">全部分类</option>
        <option v-for="cat in store.categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
      </select>
      <select class="filter-select" :value="store.filters.source_id || ''" @change="store.setFilter('source_id', $event.target.value ? Number($event.target.value) : null)">
        <option value="">全部来源</option>
        <option v-for="src in store.sources" :key="src.id" :value="src.id">{{ src.name }}</option>
      </select>
    </div>

    <div class="list-body">
      <div v-if="store.articles.length === 0" class="list-empty">
        <svg viewBox="0 0 48 48" fill="none" width="48" height="48"><rect x="6" y="6" width="36" height="36" rx="4" stroke="currentColor" stroke-width="2"/><path d="M16 18h16M16 26h12M16 34h8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
        <p>暂无文章</p>
      </div>
      <div
        v-for="article in store.articles"
        :key="article.id"
        class="article-row"
        :class="{ 'article-row--active': store.selectedArticle?.id === article.id }"
        @click="store.selectArticle(article.id)"
      >
        <div class="article-title">{{ article.title }}</div>
        <div class="article-meta">
          <span v-if="article.category" class="meta-tag">{{ article.category.name }}</span>
          <span v-if="article.source" class="meta-source">{{ article.source.name }}</span>
          <span v-if="article.author" class="meta-author">{{ article.author }}</span>
          <span class="meta-date">{{ formatDate(article.published_at || article.created_at) }}</span>
        </div>
        <div v-if="article.summary" class="article-summary">{{ article.summary }}</div>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="totalPages > 1" class="pagination">
      <button class="page-btn" :disabled="store.filters.page <= 1" @click="store.setPage(store.filters.page - 1)">‹</button>
      <span class="page-info">{{ store.filters.page }} / {{ totalPages }}</span>
      <button class="page-btn" :disabled="store.filters.page >= totalPages" @click="store.setPage(store.filters.page + 1)">›</button>
    </div>
  </div>
</template>

<script setup>
import { computed, inject } from 'vue'
import { useNewsStore } from '@/stores/news'

defineEmits(['create', 'edit'])
const store = useNewsStore()
const showCategoryManager = inject('showCategoryManager')
const showSourceManager = inject('showSourceManager')

const totalPages = computed(() => Math.ceil(store.total / store.filters.page_size) || 1)

let searchTimer = null
function debounceSearch(val) {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => store.setFilter('keyword', val), 300)
}

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('zh-CN', { year: 'numeric', month: 'short', day: 'numeric' })
}
</script>

<style scoped>
.news-list {
  width: 420px;
  min-width: 360px;
  background: var(--color-surface);
  border-right: 1px solid var(--color-border-light);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--color-border-light);
  flex-shrink: 0;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.list-title {
  font-family: var(--font-heading);
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.list-count {
  font-size: 12px;
  font-weight: 500;
  color: var(--color-text-tertiary);
  background: var(--color-surface-hover);
  padding: 2px 8px;
  border-radius: 10px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: var(--color-surface-hover);
  color: var(--color-text-secondary);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-icon:hover {
  background: var(--color-surface-active);
  color: var(--color-text);
}

.btn-create {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 18px;
  background: var(--color-accent);
  color: white;
  border: none;
  border-radius: var(--radius-pill);
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-create:hover {
  background: var(--color-accent-hover);
  transform: translateY(-1px);
}

/* 筛选栏 */
.filter-bar {
  display: flex;
  gap: 8px;
  padding: 12px 20px;
  border-bottom: 1px solid var(--color-border-light);
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  padding: 8px 14px;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-md);
  font-family: var(--font-body);
  font-size: 13px;
  color: var(--color-text);
  background: var(--color-surface);
  outline: none;
}

.search-input:focus {
  border-color: var(--color-accent);
}

.filter-select {
  padding: 8px 12px;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-md);
  font-family: var(--font-body);
  font-size: 12px;
  color: var(--color-text-secondary);
  background: var(--color-surface);
  outline: none;
  max-width: 110px;
}

.filter-select:focus {
  border-color: var(--color-accent);
}

.list-body {
  flex: 1;
  overflow-y: auto;
}

.list-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--color-text-tertiary);
  gap: 12px;
}

.list-empty p {
  font-size: 14px;
}

.article-row {
  padding: 14px 20px;
  border-bottom: 1px solid var(--color-border-light);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.article-row:hover {
  background: var(--color-surface-hover);
}

.article-row--active {
  background: var(--color-accent-subtle);
}

.article-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text);
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.3;
}

.article-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 4px;
}

.meta-tag {
  font-size: 11px;
  font-weight: 500;
  padding: 1px 7px;
  border-radius: 4px;
  background: var(--color-accent-subtle);
  color: var(--color-accent-text);
}

.meta-source {
  font-size: 11px;
  color: var(--color-info);
}

.meta-author {
  font-size: 11px;
  color: var(--color-text-tertiary);
}

.meta-date {
  font-size: 11px;
  color: var(--color-text-tertiary);
}

.article-summary {
  font-size: 12px;
  color: var(--color-text-secondary);
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

/* 分页 */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 12px;
  border-top: 1px solid var(--color-border-light);
  flex-shrink: 0;
}

.page-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  border-radius: var(--radius-sm);
  color: var(--color-text-secondary);
  font-size: 14px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.page-btn:hover:not(:disabled) {
  border-color: var(--color-accent);
  color: var(--color-accent-text);
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-info {
  font-size: 12px;
  color: var(--color-text-tertiary);
}
</style>
