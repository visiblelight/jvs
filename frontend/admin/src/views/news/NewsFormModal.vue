<template>
  <Teleport to="body">
    <div class="overlay" @click.self="$emit('close')">
      <div class="modal" @click.stop>
        <div class="modal-head">
          <h3>{{ editArticle ? '编辑文章' : '新建文章' }}</h3>
          <button class="close-btn" @click="$emit('close')">
            <svg viewBox="0 0 16 16" fill="currentColor" width="16" height="16"><path d="M3.72 3.72a.75.75 0 011.06 0L8 6.94l3.22-3.22a.75.75 0 111.06 1.06L9.06 8l3.22 3.22a.75.75 0 11-1.06 1.06L8 9.06l-3.22 3.22a.75.75 0 01-1.06-1.06L6.94 8 3.72 4.78a.75.75 0 010-1.06z"/></svg>
          </button>
        </div>

        <div class="modal-body">
          <div class="form-row">
            <label>标题 <span class="required">*</span></label>
            <input v-model="form.title" placeholder="文章标题" />
          </div>

          <div class="form-row">
            <label>简介</label>
            <input v-model="form.summary" placeholder="100字以内简要介绍" maxlength="200" />
          </div>

          <div class="form-grid">
            <div class="form-row">
              <label>分类</label>
              <select v-model="form.category_id">
                <option :value="null">无</option>
                <option v-for="cat in store.categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
              </select>
            </div>
            <div class="form-row">
              <label>来源</label>
              <select v-model="form.source_id">
                <option :value="null">无</option>
                <option v-for="src in store.sources" :key="src.id" :value="src.id">{{ src.name }}</option>
              </select>
            </div>
          </div>

          <div class="form-grid">
            <div class="form-row">
              <label>作者</label>
              <input v-model="form.author" placeholder="作者" />
            </div>
            <div class="form-row">
              <label>发表时间</label>
              <input v-model="form.published_at" type="datetime-local" />
            </div>
          </div>

          <div class="form-row">
            <label>来源 URL</label>
            <input v-model="form.source_url" placeholder="https://..." />
          </div>

          <div class="form-row">
            <label>正文 (Markdown) <span class="required">*</span></label>
            <textarea v-model="form.content" rows="12" placeholder="使用 Markdown 格式编写正文..."></textarea>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-cancel" @click="$emit('close')">取消</button>
          <button class="btn-primary" @click="handleSubmit" :disabled="!form.title || !form.content">
            {{ editArticle ? '保存' : '创建' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { reactive } from 'vue'
import { useNewsStore } from '@/stores/news'
import { createArticle, updateArticle } from '@/api/news'

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
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  animation: fadeIn 0.15s ease;
}

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.modal {
  background: var(--color-surface);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  width: 680px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-overlay);
  animation: slideUp 0.2s ease;
}

@keyframes slideUp { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }

.modal-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--color-border-light);
  flex-shrink: 0;
}

.modal-head h3 {
  font-family: var(--font-heading);
  font-size: 17px;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.close-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: none;
  color: var(--color-text-tertiary);
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.close-btn:hover {
  background: var(--color-surface-hover);
  color: var(--color-text);
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
}

.form-row {
  margin-bottom: 16px;
}

.form-row label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary);
  margin-bottom: 6px;
}

.required {
  color: var(--color-danger);
}

.form-row input,
.form-row select,
.form-row textarea {
  width: 100%;
  padding: 9px 12px;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-family: var(--font-body);
  font-size: 13px;
  color: var(--color-text);
  background: var(--color-surface);
  outline: none;
  transition: border-color var(--transition-fast);
}

.form-row input:focus,
.form-row select:focus,
.form-row textarea:focus {
  border-color: var(--color-accent);
}

.form-row textarea {
  resize: vertical;
  line-height: 1.6;
  font-family: 'SF Mono', 'Fira Code', monospace, var(--font-body);
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 16px 24px;
  border-top: 1px solid var(--color-border-light);
  flex-shrink: 0;
}

.btn-cancel {
  padding: 8px 18px;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  border-radius: var(--radius-sm);
  font-family: var(--font-body);
  font-size: 13px;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-cancel:hover {
  background: var(--color-surface-hover);
}

.btn-primary {
  padding: 8px 20px;
  background: var(--color-accent);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-accent-hover);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
