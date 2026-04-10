<template>
  <div class="news-detail">
    <div v-if="!store.selectedArticle" class="detail-empty">
      <svg viewBox="0 0 48 48" fill="none" width="56" height="56"><rect x="8" y="6" width="32" height="36" rx="3" stroke="currentColor" stroke-width="1.5"/><path d="M16 16h16M16 24h12M16 32h8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
      <p>选择一篇文章查看详情</p>
    </div>

    <template v-else>
      <div class="detail-header">
        <div class="detail-actions">
          <button class="action-btn" @click="$emit('edit', store.selectedArticle)">
            <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14"><path d="M11.013 1.427a1.75 1.75 0 012.474 0l1.086 1.086a1.75 1.75 0 010 2.474l-8.61 8.61c-.21.21-.47.364-.756.445l-3.251.93a.75.75 0 01-.927-.928l.929-3.25a1.75 1.75 0 01.445-.758l8.61-8.61zm1.414 1.06a.25.25 0 00-.354 0L3.463 11.1a.25.25 0 00-.064.108l-.563 1.97 1.97-.563a.25.25 0 00.108-.064l8.61-8.61a.25.25 0 000-.354L12.427 2.488z"/></svg>
            编辑
          </button>
          <button class="action-btn action-btn--danger" @click="handleDelete">
            <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14"><path d="M6.5 1.75a.25.25 0 01.25-.25h2.5a.25.25 0 01.25.25V3h-3V1.75zM11 3V1.75A1.75 1.75 0 009.25 0h-2.5A1.75 1.75 0 005 1.75V3H2.75a.75.75 0 000 1.5h.31l.727 9.46A1.75 1.75 0 005.536 15.5h4.928a1.75 1.75 0 001.749-1.54l.727-9.46h.31a.75.75 0 000-1.5H11zm-5.47 3.23a.75.75 0 011.06 0L8 7.64l1.41-1.41a.75.75 0 111.06 1.06L9.06 8.7l1.41 1.41a.75.75 0 11-1.06 1.06L8 9.76l-1.41 1.41a.75.75 0 01-1.06-1.06L6.94 8.7 5.53 7.29a.75.75 0 010-1.06z"/></svg>
            删除
          </button>
        </div>
      </div>

      <div class="detail-body">
        <h1 class="article-title">{{ store.selectedArticle.title }}</h1>

        <div class="article-info">
          <span v-if="store.selectedArticle.category" class="info-badge info-badge--category">{{ store.selectedArticle.category.name }}</span>
          <span v-if="store.selectedArticle.source" class="info-item">
            <svg viewBox="0 0 16 16" fill="currentColor" width="12" height="12"><path d="M8 0a8 8 0 100 16A8 8 0 008 0z"/></svg>
            {{ store.selectedArticle.source.name }}
          </span>
          <span v-if="store.selectedArticle.author" class="info-item">
            <svg viewBox="0 0 16 16" fill="currentColor" width="12" height="12"><path d="M10.561 8.073a6 6 0 01-3.32 0A5.996 5.996 0 002 14h12a5.996 5.996 0 00-5.239-5.927zM8 7a3 3 0 100-6 3 3 0 000 6z"/></svg>
            {{ store.selectedArticle.author }}
          </span>
          <span class="info-item">
            <svg viewBox="0 0 16 16" fill="currentColor" width="12" height="12"><path d="M4.75 0a.75.75 0 01.75.75V2h5V.75a.75.75 0 011.5 0V2H14a1 1 0 011 1v11a2 2 0 01-2 2H3a2 2 0 01-2-2V3a1 1 0 011-1h1.75V.75A.75.75 0 014.75 0z"/></svg>
            {{ formatDate(store.selectedArticle.published_at || store.selectedArticle.created_at) }}
          </span>
          <a v-if="store.selectedArticle.source_url" :href="store.selectedArticle.source_url" target="_blank" class="info-link">
            <svg viewBox="0 0 16 16" fill="currentColor" width="12" height="12"><path d="M4.715 6.542L3.343 7.914a3 3 0 104.243 4.243l1.828-1.829A3 3 0 008.586 5.5l-.793.793a.5.5 0 00.353.854 2 2 0 01.586 3.536l-1.829 1.829a2 2 0 01-2.828-2.829l1.372-1.372a.5.5 0 00-.354-.853zm6.57-4.085a3 3 0 00-4.243 0L5.214 4.285a3 3 0 00.828 4.828l.793-.793a.5.5 0 00-.353-.854 2 2 0 01-.586-3.536l1.829-1.829a2 2 0 012.828 2.829l-1.372 1.372a.5.5 0 00.354.853h.001a3 3 0 002.55-1.457z"/></svg>
            原文链接
          </a>
        </div>

        <div v-if="store.selectedArticle.summary" class="article-summary">
          {{ store.selectedArticle.summary }}
        </div>

        <div class="article-content markdown-body" v-html="renderedContent"></div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useDialog } from '@/composables/useDialog'
const { confirm } = useDialog()
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { useNewsStore } from '@/stores/news'
import { deleteArticle } from '@/api/news'

defineEmits(['edit'])
const store = useNewsStore()

const renderedContent = computed(() => {
  if (!store.selectedArticle?.content) return ''
  return DOMPurify.sanitize(marked(store.selectedArticle.content, { breaks: true }))
})

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}

async function handleDelete() {
  if (!await confirm('确定要永久删除这篇文章吗？此操作不可逆。', { title: '删除文章', danger: true })) return
  await deleteArticle(store.selectedArticle.id)
  store.selectedArticle = null
  await store.fetchArticles()
}
</script>

<style scoped>
.news-detail {
  flex: 1;
  min-width: 0;
  background: var(--color-surface);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.detail-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--color-text-tertiary);
  gap: 16px;
}

.detail-empty p {
  font-size: 14px;
}

.detail-header {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 12px 24px;
  border-bottom: 1px solid var(--color-border-light);
  flex-shrink: 0;
}

.detail-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 16px;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  border-radius: var(--radius-pill);
  font-family: var(--font-body);
  font-size: 12px;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.action-btn:hover {
  border-color: var(--color-accent);
  color: var(--color-accent-text);
}

.action-btn--danger:hover {
  border-color: var(--color-danger);
  color: var(--color-danger);
}

.detail-body {
  flex: 1;
  overflow-y: auto;
  padding: 28px 32px;
}

.article-title {
  font-family: var(--font-heading);
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text);
  line-height: 1.3;
  margin: 0 0 16px;
}

.article-info {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--color-border-light);
}

.info-badge {
  font-size: 12px;
  font-weight: 500;
  padding: 2px 10px;
  border-radius: 4px;
}

.info-badge--category {
  background: var(--color-accent-subtle);
  color: var(--color-accent-text);
}

.info-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 13px;
  color: var(--color-text-secondary);
}

.info-item svg {
  opacity: 0.5;
}

.info-link {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 13px;
  color: var(--color-accent-text);
  transition: opacity var(--transition-fast);
}

.info-link:hover {
  opacity: 0.75;
}

.article-summary {
  font-size: 14px;
  color: var(--color-text-secondary);
  line-height: 1.7;
  padding: 14px 16px;
  background: var(--color-surface-hover);
  border-radius: var(--radius-md);
  margin-bottom: 24px;
  border-left: 3px solid var(--color-accent);
  white-space: pre-wrap;
}

/* Markdown Content */
.markdown-body {
  font-size: 15px;
  line-height: 1.8;
  color: var(--color-text);
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3),
.markdown-body :deep(h4) {
  font-family: var(--font-heading);
  font-weight: 600;
  color: var(--color-text);
  margin: 24px 0 12px;
  line-height: 1.3;
}

.markdown-body :deep(h1) { font-size: 22px; }
.markdown-body :deep(h2) { font-size: 19px; }
.markdown-body :deep(h3) { font-size: 16px; }

.markdown-body :deep(p) {
  margin: 0 0 14px;
}

.markdown-body :deep(a) {
  color: var(--color-accent-text);
  text-decoration: underline;
  text-underline-offset: 2px;
}

.markdown-body :deep(code) {
  font-size: 13px;
  padding: 2px 6px;
  background: var(--color-surface-hover);
  border-radius: 4px;
}

.markdown-body :deep(pre) {
  background: var(--color-surface-hover);
  padding: 16px;
  border-radius: var(--radius-md);
  overflow-x: auto;
  margin: 0 0 14px;
}

.markdown-body :deep(pre code) {
  padding: 0;
  background: none;
}

.markdown-body :deep(blockquote) {
  margin: 0 0 14px;
  padding: 12px 16px;
  border-left: 3px solid var(--color-border);
  color: var(--color-text-secondary);
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  margin: 0 0 14px;
  padding-left: 24px;
}

.markdown-body :deep(li) {
  margin-bottom: 4px;
}

.markdown-body :deep(img) {
  max-width: 100%;
  border-radius: var(--radius-md);
  margin: 8px 0;
  display: block;
  box-shadow: var(--shadow-sm);
}

.markdown-body :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 0 0 14px;
}

.markdown-body :deep(th),
.markdown-body :deep(td) {
  padding: 8px 12px;
  border: 1px solid var(--color-border);
  text-align: left;
}

.markdown-body :deep(th) {
  background: var(--color-surface-hover);
  font-weight: 600;
}

.markdown-body :deep(hr) {
  border: none;
  border-top: 1px solid var(--color-border-light);
  margin: 24px 0;
}
</style>
