<template>
  <div class="detail-page">
    <PageHeader :title="article?.title ? '' : '文章'" back-to="/news" />

    <div v-if="loading" class="loading-wrap">
      <div class="spinner" />
    </div>

    <div v-else-if="article" class="detail-body">
      <div class="article-meta">
        <span v-if="article.category" class="cat-badge">{{ article.category.name }}</span>
        <span class="meta-date">{{ formatDate(article.published_at || article.created_at) }}</span>
        <span v-if="article.source" class="meta-source">{{ article.source.name }}</span>
        <a v-if="article.source_url" :href="article.source_url" target="_blank" class="meta-link">原文</a>
      </div>

      <h1 class="article-title">{{ article.title }}</h1>

      <div v-if="article.summary" class="article-summary">{{ article.summary }}</div>

      <div class="article-content" v-html="renderedContent" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { marked } from 'marked'
import { getArticle } from '@/api/news'
import PageHeader from '@/components/PageHeader.vue'

const route = useRoute()
const article = ref(null)
const loading = ref(true)

const renderedContent = computed(() => {
  if (!article.value?.content) return ''
  return marked(article.value.content, { breaks: true })
})

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}

onMounted(async () => {
  try {
    const { data } = await getArticle(route.params.id)
    article.value = data
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.detail-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
}

.loading-wrap {
  flex: 1; display: flex; align-items: center; justify-content: center;
}

.spinner {
  width: 32px; height: 32px;
  border: 2.5px solid var(--color-border);
  border-top-color: var(--color-accent);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.detail-body {
  flex: 1; overflow-y: auto;
  padding: 20px 20px 40px;
}

.article-meta {
  display: flex; flex-wrap: wrap; align-items: center;
  gap: 8px; margin-bottom: 14px;
}

.cat-badge {
  font-size: 11px; font-weight: 500; padding: 2px 8px;
  background: var(--color-accent-subtle); color: var(--color-accent-text);
  border-radius: var(--radius-full);
}

.meta-date, .meta-source { font-size: 12px; color: var(--color-text-tertiary); }

.meta-link {
  font-size: 12px; color: var(--color-accent-text);
  text-decoration: underline; text-underline-offset: 2px;
}

.article-title {
  font-size: 22px; font-weight: 700;
  color: var(--color-text);
  line-height: 1.35;
  letter-spacing: -0.5px;
  margin-bottom: 16px;
}

.article-summary {
  font-size: 14px; color: var(--color-text-secondary);
  line-height: 1.7; padding: 14px 16px;
  background: var(--color-bg);
  border-radius: var(--radius-md);
  border-left: 3px solid var(--color-accent);
  margin-bottom: 20px;
  white-space: pre-wrap;
}

.article-content {
  font-size: 15px; line-height: 1.85;
  color: var(--color-text);
}

.article-content :deep(p)         { margin-bottom: 14px; }
.article-content :deep(h1),
.article-content :deep(h2),
.article-content :deep(h3)        { font-weight: 700; margin: 24px 0 10px; line-height: 1.3; color: var(--color-text); }
.article-content :deep(h1)        { font-size: 20px; }
.article-content :deep(h2)        { font-size: 18px; }
.article-content :deep(h3)        { font-size: 16px; }
.article-content :deep(a)         { color: var(--color-accent-text); text-decoration: underline; }
.article-content :deep(code)      { font-size: 13px; padding: 1px 6px; background: var(--color-bg); border-radius: 4px; }
.article-content :deep(pre)       { background: var(--color-bg); padding: 14px; border-radius: var(--radius-md); overflow-x: auto; margin-bottom: 14px; }
.article-content :deep(pre code)  { padding: 0; background: none; }
.article-content :deep(blockquote){ border-left: 3px solid var(--color-border); padding: 10px 14px; color: var(--color-text-secondary); margin-bottom: 14px; }
.article-content :deep(ul),
.article-content :deep(ol)        { padding-left: 20px; margin-bottom: 14px; }
.article-content :deep(img)       { max-width: 100%; border-radius: var(--radius-md); }
</style>
