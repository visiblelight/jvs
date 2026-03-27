<template>
  <Teleport to="body">
    <div class="drawer-overlay" @click.self="$emit('close')">
      <div class="drawer-panel" @click.stop>
        <div class="drawer-head">
          <h3>{{ editArticle ? '编辑文章' : '新建文章' }}</h3>
          <button class="close-btn active-scale" @click="$emit('close')">
            <svg viewBox="0 0 16 16" fill="currentColor" width="20" height="20">
              <path d="M3.72 3.72a.75.75 0 011.06 0L8 6.94l3.22-3.22a.75.75 0 111.06 1.06L9.06 8l3.22 3.22a.75.75 0 11-1.06 1.06L8 9.06l-3.22 3.22a.75.75 0 01-1.06-1.06L6.94 8 3.72 4.78a.75.75 0 010-1.06z"/>
            </svg>
          </button>
        </div>

        <div class="drawer-body">
          <div class="field title-field">
            <input v-model="form.title" type="text" placeholder="文章标题..." required class="large-input" />
          </div>

          <div class="field">
            <textarea v-model="form.summary" rows="2" placeholder="填写100字以内简要介绍..."></textarea>
          </div>

          <div class="field-row">
            <div class="field-section">
              <label>新闻分类</label>
              <select v-model="form.category_id" class="minimal-select">
                <option :value="null">未选择分类</option>
                <option v-for="cat in store.categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
              </select>
            </div>
            <div class="field-section">
              <label>信息来源</label>
              <select v-model="form.source_id" class="minimal-select">
                <option :value="null">未知来源</option>
                <option v-for="src in store.sources" :key="src.id" :value="src.id">{{ src.name }}</option>
              </select>
            </div>
          </div>

          <div class="field-row">
            <div class="field-section">
              <label>作者笔名</label>
              <input v-model="form.author" type="text" placeholder="匿名" class="minimal-select" />
            </div>
            <div class="field-section">
              <label>首发时间</label>
              <input v-model="form.published_at" type="datetime-local" class="minimal-select" />
            </div>
          </div>

          <div class="field-section">
            <label>原始链接 (可选)</label>
            <input v-model="form.source_url" type="url" placeholder="https://..." class="minimal-select" />
          </div>

          <div class="field-section" style="flex: 1; display: flex; flex-direction: column;">
            <label>正文 (Markdown 语法) <span class="required">*</span></label>
            <textarea
              ref="contentEl"
              v-model="form.content"
              class="markdown-editor"
              placeholder="在此输入 Markdown 格式的文章正文... （可 Ctrl+V 粘贴图片）"
              @paste="handlePaste"
            ></textarea>
          </div>
        </div>

        <div class="drawer-foot">
          <button type="button" class="btn-secondary active-scale" @click="$emit('close')">取消</button>
          <button type="button" class="btn-primary active-scale" @click="handleSubmit" :disabled="!form.title || !form.content">
            {{ editArticle ? '保存更改' : '发布文章' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useNewsStore } from '@/stores/news'
import { createArticle, updateArticle } from '@/api/news'
import { useImagePaste } from '@/composables/useImagePaste'

const contentEl = ref(null)
const { handlePaste } = useImagePaste({
  module: 'news',
  getValue: () => form.content,
  setValue: (val) => { form.content = val },
  getEl: () => contentEl.value,
})

const props = defineProps({
  editArticle: { type: Object, default: null },
})
const emit = defineEmits(['close', 'saved'])
const store = useNewsStore()

function formatLocalDatetime(d) {
  if (!d) return ''
  const dt = new Date(d)
  const pad = (n) => String(n).padStart(2, '0')
  return `${dt.getFullYear()}-${pad(dt.getMonth() + 1)}-${pad(dt.getDate())}T${pad(dt.getHours())}:${pad(dt.getMinutes())}`
}

const form = reactive({
  title: props.editArticle?.title || '',
  summary: props.editArticle?.summary || '',
  content: props.editArticle?.content || '',
  source_url: props.editArticle?.source_url || '',
  source_id: props.editArticle?.source_id || null,
  author: props.editArticle?.author || '',
  published_at: formatLocalDatetime(props.editArticle?.published_at) || '',
  category_id: props.editArticle?.category_id || null,
})

async function handleSubmit() {
  const data = { ...form }
  if (!data.published_at) data.published_at = null
  else data.published_at = new Date(data.published_at).toISOString()

  if (props.editArticle) {
    await updateArticle(props.editArticle.id, data)
  } else {
    await createArticle(data)
  }
  emit('saved')
}
</script>

<style scoped>
.drawer-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 28px;
  border-bottom: 1px solid var(--color-border);
}

.drawer-head h3 {
  font-family: var(--font-heading);
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text);
  margin: 0;
}

.close-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: var(--color-bg-base);
  color: var(--color-text-secondary);
  cursor: pointer;
  border-radius: var(--radius-pill);
}

.close-btn:hover {
  color: var(--color-text);
}

.drawer-body {
  flex: 1;
  padding: 24px 28px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.title-field .large-input {
  font-size: 24px;
  font-weight: 800;
  font-family: var(--font-heading);
  padding: 0;
  border: none;
  background: transparent;
  width: 100%;
  color: var(--color-text);
  outline: none;
}
.title-field .large-input::placeholder {
  color: var(--color-text-tertiary);
  font-weight: 700;
}

.field textarea {
  width: 100%;
  padding: 14px 18px;
  border: 1px solid transparent;
  background: var(--color-bg-base);
  border-radius: var(--radius-md);
  color: var(--color-text);
  font-size: 14px;
  outline: none;
  resize: vertical;
  transition: all var(--transition-fast);
}
.field textarea:focus {
  background: transparent;
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px var(--color-accent-subtle);
}

.field-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.field-section label {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
}

.required {
  color: var(--color-danger);
  margin-left: 4px;
}

.field-row {
  display: flex;
  gap: 16px;
}
.field-row > div {
  flex: 1;
}

.minimal-select {
  height: 40px;
  padding: 0 14px;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: var(--color-bg-base);
  color: var(--color-text);
  font-size: 13px;
  font-weight: 500;
  outline: none;
  transition: all var(--transition-fast);
  width: 100%;
}
.minimal-select:focus {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px var(--color-accent-subtle);
}
.minimal-select::placeholder {
  color: var(--color-text-tertiary);
}

.markdown-editor {
  flex: 1;
  min-height: 200px;
  width: 100%;
  padding: 16px 20px;
  border: 1px solid var(--color-border);
  background: var(--color-bg-base);
  border-radius: var(--radius-md);
  color: var(--color-text);
  font-size: 13px;
  font-family: 'SF Mono', 'Fira Code', 'Courier New', Courier, monospace;
  outline: none;
  resize: none;
  transition: all var(--transition-fast);
  line-height: 1.6;
}
.markdown-editor:focus {
  border-color: var(--color-accent);
  background: transparent;
  box-shadow: 0 0 0 3px var(--color-accent-subtle);
}
.markdown-editor::placeholder {
  color: var(--color-text-tertiary);
}

.drawer-foot {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 24px 28px;
  border-top: 1px solid var(--color-border);
  background: var(--color-surface);
}

.btn-secondary {
  padding: 10px 24px;
  border: 1px solid transparent;
  background: var(--color-bg-base);
  color: var(--color-text-secondary);
  border-radius: var(--radius-pill);
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
}
.btn-secondary:hover {
  color: var(--color-text);
  background: rgba(0,0,0,0.05);
}

.btn-primary {
  padding: 10px 28px;
  background: var(--color-accent);
  color: white;
  border: none;
  border-radius: var(--radius-pill);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}
.btn-primary:hover:not(:disabled) {
  background: var(--color-accent-hover);
}
.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
