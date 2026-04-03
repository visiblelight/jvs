<template>
  <div class="todo-detail" v-if="store.currentItem">
    <div class="detail-header">
      <h3 class="detail-title">{{ store.currentItem.title }}</h3>
      <div class="detail-actions">
          <button class="act-btn act-btn--edit" @click="$emit('edit', store.currentItem)">
            <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14"><path d="M11.013 1.427a1.75 1.75 0 012.474 0l1.086 1.086a1.75 1.75 0 010 2.474l-8.61 8.61c-.21.21-.47.364-.756.445l-3.251.93a.75.75 0 01-.927-.928l.929-3.25a1.75 1.75 0 01.445-.758l8.61-8.61zm1.414 1.06a.25.25 0 00-.354 0L3.463 11.098a.25.25 0 00-.064.108l-.558 1.953 1.953-.558a.25.25 0 00.108-.064l8.61-8.61a.25.25 0 000-.354l-1.086-1.086z"/></svg>
            编辑
          </button>
          <button v-if="store.currentItem.status === 'completed'" class="act-btn act-btn--archive" @click="handleArchive">
            <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14"><path d="M1.75 2.5h12.5a.25.25 0 01.25.25v1.5a.25.25 0 01-.25.25H1.75a.25.25 0 01-.25-.25v-1.5a.25.25 0 01.25-.25zM0 2.75C0 1.784.784 1 1.75 1h12.5c.966 0 1.75.784 1.75 1.75v1.5A1.75 1.75 0 0114.25 6H1.75A1.75 1.75 0 010 4.25v-1.5zM1.75 7a.75.75 0 00-.75.75v5.5c0 .966.784 1.75 1.75 1.75h10.5A1.75 1.75 0 0015 13.25v-5.5a.75.75 0 00-1.5 0v5.5a.25.25 0 01-.25.25H2.75a.25.25 0 01-.25-.25v-5.5A.75.75 0 001.75 7zM6 9.25a.75.75 0 01.75-.75h2.5a.75.75 0 010 1.5h-2.5a.75.75 0 01-.75-.75z"/></svg>
            归档
          </button>
          <button v-if="store.currentItem.status === 'archived'" class="act-btn act-btn--archive" @click="handleUnarchive">
            <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14"><path d="M1.75 2.5h12.5a.25.25 0 01.25.25v1.5a.25.25 0 01-.25.25H1.75a.25.25 0 01-.25-.25v-1.5a.25.25 0 01.25-.25zM0 2.75C0 1.784.784 1 1.75 1h12.5c.966 0 1.75.784 1.75 1.75v1.5A1.75 1.75 0 0114.25 6H1.75A1.75 1.75 0 010 4.25v-1.5zM1.75 7a.75.75 0 00-.75.75v5.5c0 .966.784 1.75 1.75 1.75h10.5A1.75 1.75 0 0015 13.25v-5.5a.75.75 0 00-1.5 0v5.5a.25.25 0 01-.25.25H2.75a.25.25 0 01-.25-.25v-5.5A.75.75 0 001.75 7zM6 9.25a.75.75 0 01.75-.75h2.5a.75.75 0 010 1.5h-2.5a.75.75 0 01-.75-.75z"/></svg>
            取消归档
          </button>
          <button class="act-btn act-btn--danger" @click="handleDelete">
            <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14"><path d="M6.5 1.75a.25.25 0 01.25-.25h2.5a.25.25 0 01.25.25V3h-3V1.75zm4.5 0V3h2.25a.75.75 0 010 1.5H2.75a.75.75 0 010-1.5H5V1.75C5 .784 5.784 0 6.75 0h2.5C10.216 0 11 .784 11 1.75zM4.496 6.675a.75.75 0 10-1.492.15l.66 6.6A1.75 1.75 0 005.405 15h5.19a1.75 1.75 0 001.741-1.575l.66-6.6a.75.75 0 00-1.492-.15l-.66 6.6a.25.25 0 01-.249.225h-5.19a.25.25 0 01-.249-.225l-.66-6.6z"/></svg>
            删除
          </button>
      </div>
    </div>

    <div class="detail-body">
      <div class="desc-section" v-if="store.currentItem.description">
        <span class="prop-label">描述</span>
        <div class="desc-block markdown-body" v-html="renderMarkdown(store.currentItem.description)"></div>
      </div>

      <div class="prop">
        <span class="prop-label">状态</span>
        <select class="prop-select" :value="store.currentItem.status" @change="handleStatusChange">
          <option value="pending">未完成</option>
          <option value="paused">暂停中</option>
          <option value="completed">已完成</option>
          <option value="archived">已归档</option>
        </select>
      </div>

      <div class="prop">
        <span class="prop-label">优先级</span>
        <div class="level-dots">
          <span class="detail-badge" :class="'priority-' + store.currentItem.priority">{{ getPriorityLabel(store.currentItem.priority) }}</span>
        </div>
      </div>

      <div class="prop">
        <span class="prop-label">重要程度</span>
        <div class="level-dots">
          <span class="detail-badge">{{ getImportanceLabel(store.currentItem.importance) }}</span>
        </div>
      </div>

      <div class="prop">
        <span class="prop-label">截止时间</span>
        <span class="prop-value" :class="{ overdue: isOverdue }">{{ formatDate(store.currentItem.due_date) || '—' }}</span>
      </div>

      <div v-if="store.currentItem.scheduled_at" class="prop">
        <span class="prop-label">🕐 执行时间</span>
        <span class="prop-value" style="color: var(--color-accent-text);">{{ formatDate(store.currentItem.scheduled_at) }}</span>
      </div>

      <div class="prop">
        <span class="prop-label">创建时间</span>
        <span class="prop-value">{{ formatDate(store.currentItem.created_at) }}</span>
      </div>

      <div v-if="store.currentItem.completed_at" class="prop">
        <span class="prop-label">完成时间</span>
        <span class="prop-value">{{ formatDate(store.currentItem.completed_at) }}</span>
      </div>

      <div v-if="store.currentItem.archived_at" class="prop">
        <span class="prop-label">归档时间</span>
        <span class="prop-value">{{ formatDate(store.currentItem.archived_at) }}</span>
      </div>

      <div class="prop" v-if="store.currentItem.tags.length">
        <span class="prop-label">标签</span>
        <div class="detail-tags">
          <span
            v-for="tag in store.currentItem.tags"
            :key="tag.id"
            class="detail-tag"
            :style="{ '--tag-color': tag.color }"
          >{{ tag.name }}</span>
        </div>
      </div>

    </div>

    <!-- 评论区 -->
    <div class="comment-section">
      <div class="comment-section-header">
        <span class="comment-section-title">评论</span>
        <span v-if="comments.length" class="comment-count-badge">{{ comments.length }}</span>
      </div>

      <div class="comment-list" ref="commentListRef">
        <div
          v-for="comment in comments"
          :key="comment.id"
          class="comment-item"
          @mouseenter="comment._hover = true"
          @mouseleave="comment._hover = false"
        >
          <div class="comment-avatar">
            <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16"><path d="M12 12c2.7 0 4.8-2.1 4.8-4.8S14.7 2.4 12 2.4 7.2 4.5 7.2 7.2 9.3 12 12 12zm0 2.4c-3.2 0-9.6 1.6-9.6 4.8v2.4h19.2v-2.4c0-3.2-6.4-4.8-9.6-4.8z"/></svg>
          </div>
          <div class="comment-body">
            <div class="comment-meta">
              <span class="comment-time" :title="formatDateFull(comment.created_at)">{{ timeAgo(comment.created_at) }}</span>
              <span v-if="comment.updated_at !== comment.created_at" class="comment-edited">已编辑</span>
              <span class="comment-actions" :class="{ 'comment-actions--visible': comment._hover && editingCommentId !== comment.id }">
                <button class="comment-act-btn" @click="startEdit(comment)">编辑</button>
                <button class="comment-act-btn comment-act-btn--danger" @click="confirmDeleteComment(comment)">删除</button>
              </span>
            </div>
            <div v-if="editingCommentId !== comment.id" class="comment-content markdown-body" v-html="renderMarkdown(comment.content)"></div>
            <div v-else class="comment-edit-area">
              <textarea
                v-model="editingContent"
                class="comment-textarea"
                @keydown.esc="cancelEdit"
                @keydown.enter.meta.prevent="saveEdit(comment)"
                @keydown.enter.ctrl.prevent="saveEdit(comment)"
                ref="editTextareaRef"
                rows="3"
              ></textarea>
              <div class="comment-edit-actions">
                <button class="comment-save-btn" @click="saveEdit(comment)">保存</button>
                <button class="comment-cancel-btn" @click="cancelEdit">取消</button>
              </div>
            </div>
          </div>
        </div>
        <div v-if="comments.length === 0" class="comment-empty">暂无评论</div>
      </div>

      <div class="comment-input-area">
        <textarea
          v-model="newComment"
          class="comment-textarea"
          placeholder="添加评论…支持 Markdown，可粘贴图片"
          @keydown.meta.enter.prevent="submitComment"
          @keydown.ctrl.enter.prevent="submitComment"
          @paste="handlePaste"
          ref="newCommentRef"
          rows="3"
        ></textarea>
        <div class="comment-input-foot">
          <span class="comment-hint">⌘ Enter 发送</span>
          <button class="comment-submit-btn" :disabled="!newComment.trim() || submitting" @click="submitComment">
            {{ submitting ? '发送中…' : '发送' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Custom Confirm Modal -->
    <Teleport to="body">
      <div v-if="confirmDialog.show" class="modal-overlay" @click.self="cancelConfirm">
        <div class="confirm-modal active-scale" @click.stop>
          <div class="confirm-body">
            <h3>确认删除</h3>
            <p>{{ confirmDialog.message }}</p>
          </div>
          <div class="confirm-foot">
            <button class="btn-cancel active-scale" @click="cancelConfirm">取消</button>
            <button class="btn-danger active-scale" @click="executeConfirm">{{ confirmDialog.confirmText }}</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
  <div class="todo-detail todo-detail--empty" v-else>
    <svg viewBox="0 0 48 48" fill="none" width="40" height="40"><circle cx="24" cy="24" r="20" stroke="currentColor" stroke-width="1.5"/><path d="M18 24h12M24 18v12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
    <p>选择一个事项查看详情</p>
  </div>
</template>

<script setup>
import { computed, ref, watch, nextTick } from 'vue'
import { useTodoStore } from '@/stores/todo'
import { updateItemStatus, deleteItem, getComments, createComment, updateComment, deleteComment } from '@/api/todo'
import { uploadImage } from '@/api/uploads'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

function renderMarkdown(text) {
  if (!text) return ''
  return DOMPurify.sanitize(marked.parse(text))
}

defineEmits(['edit'])

const store = useTodoStore()

const priorities = ['极低', '低', '中等', '高', '极高']
const importances = ['不重要', '一般', '偏重要', '非常重要', '极其重要']
const getPriorityLabel = (n) => priorities[n - 1] || '无'
const getImportanceLabel = (n) => importances[n - 1] || '无'

// --- Custom Confirm Modal Logic ---
const confirmDialog = ref({
  show: false,
  message: '',
  actionCb: null,
  confirmText: '确认删除',
})

function customConfirm(message, callback, confirmText = '确认删除') {
  confirmDialog.value = { show: true, message, actionCb: callback, confirmText }
}

function executeConfirm() {
  if (confirmDialog.value.actionCb) confirmDialog.value.actionCb()
  confirmDialog.value.show = false
}

function cancelConfirm() {
  confirmDialog.value.show = false
}

const isOverdue = computed(() => {
  const item = store.currentItem
  return item?.due_date && item.status !== 'completed' && new Date(item.due_date) < new Date()
})

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleString('zh-CN', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function formatDateFull(d) {
  if (!d) return ''
  return new Date(d).toLocaleString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

function timeAgo(d) {
  if (!d) return ''
  const diff = Date.now() - new Date(d).getTime()
  const min = Math.floor(diff / 60000)
  if (min < 1) return '刚刚'
  if (min < 60) return `${min} 分钟前`
  const hr = Math.floor(min / 60)
  if (hr < 24) return `${hr} 小时前`
  const day = Math.floor(hr / 24)
  if (day < 30) return `${day} 天前`
  return formatDate(d)
}

async function handleStatusChange(e) {
  await updateItemStatus(store.currentItem.id, e.target.value)
  await store.fetchItems()
  await store.selectItem(store.currentItem.id)
}

async function handleArchive() {
  await updateItemStatus(store.currentItem.id, 'archived')
  await store.fetchItems()
  await store.selectItem(store.currentItem.id)
}

async function handleUnarchive() {
  await updateItemStatus(store.currentItem.id, 'completed')
  await store.fetchItems()
  await store.selectItem(store.currentItem.id)
}

function handleDelete() {
  customConfirm(`确认将事项「${store.currentItem.title}」移至垃圾桶吗？您可以在垃圾桶找回它。`, async () => {
    await deleteItem(store.currentItem.id)
    store.currentItem = null
    await store.fetchItems()
  })
}

// ── 评论 ──
const comments = ref([])
const newComment = ref('')
const submitting = ref(false)
const editingCommentId = ref(null)
const editingContent = ref('')
const commentListRef = ref(null)
const newCommentRef = ref(null)
const editTextareaRef = ref(null)

watch(() => store.currentItem?.id, async (id) => {
  comments.value = []
  editingCommentId.value = null
  if (id) await loadComments(id)
}, { immediate: true })

async function loadComments(itemId) {
  const res = await getComments(itemId)
  comments.value = res.data.map(c => ({ ...c, _hover: false }))
}

async function submitComment() {
  const content = newComment.value.trim()
  if (!content || submitting.value) return
  submitting.value = true
  try {
    await createComment(store.currentItem.id, { content })
    newComment.value = ''
    await loadComments(store.currentItem.id)
    await store.selectItem(store.currentItem.id) // refresh comment_count
    await nextTick()
    scrollCommentsToBottom()
  } finally {
    submitting.value = false
  }
}

function scrollCommentsToBottom() {
  if (commentListRef.value) {
    commentListRef.value.scrollTop = commentListRef.value.scrollHeight
  }
}

function startEdit(comment) {
  editingCommentId.value = comment.id
  editingContent.value = comment.content
  nextTick(() => {
    if (editTextareaRef.value) {
      const el = Array.isArray(editTextareaRef.value) ? editTextareaRef.value[0] : editTextareaRef.value
      el?.focus()
    }
  })
}

function cancelEdit() {
  editingCommentId.value = null
  editingContent.value = ''
}

async function saveEdit(comment) {
  const content = editingContent.value.trim()
  if (!content) return
  await updateComment(store.currentItem.id, comment.id, { content })
  cancelEdit()
  await loadComments(store.currentItem.id)
}

function confirmDeleteComment(comment) {
  customConfirm('确认删除这条评论吗？', async () => {
    await deleteComment(store.currentItem.id, comment.id)
    await loadComments(store.currentItem.id)
    await store.selectItem(store.currentItem.id) // refresh comment_count
  })
}

async function handlePaste(e) {
  const items = e.clipboardData?.items
  if (!items) return
  for (const item of items) {
    if (item.type.startsWith('image/')) {
      e.preventDefault()
      const file = item.getAsFile()
      const placeholder = '![上传中…]()'
      const textarea = newCommentRef.value
      const pos = textarea.selectionStart
      newComment.value = newComment.value.slice(0, pos) + placeholder + newComment.value.slice(pos)
      try {
        const res = await uploadImage(file, 'todo')
        const url = res.data.url
        newComment.value = newComment.value.replace(placeholder, `![图片](${url})`)
      } catch {
        newComment.value = newComment.value.replace(placeholder, '')
      }
      break
    }
  }
}
</script>

<style scoped>
.todo-detail {
  width: 360px;
  background: var(--color-surface);
  overflow-y: auto;
  flex-shrink: 0;
}

.todo-detail--empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--color-text-tertiary);
  gap: 12px;
  font-size: 14px;
}

.detail-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 20px;
  border-bottom: 1px solid var(--color-border-light);
  gap: 12px;
}

.detail-title {
  font-family: var(--font-heading);
  font-size: 17px;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
  flex: 1;
  word-break: break-word;
  line-height: 1.4;
}

.detail-actions {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

.act-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 6px 14px;
  border: 1px solid var(--color-border);
  background: none;
  border-radius: var(--radius-pill);
  font-family: var(--font-body);
  font-size: 12px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.act-btn--edit {
  color: var(--color-accent-text);
}

.act-btn--edit:hover {
  border-color: var(--color-accent);
  background: var(--color-accent-subtle);
}

.act-btn--archive {
  color: var(--color-text-secondary);
}

.act-btn--archive:hover {
  border-color: var(--color-text-tertiary);
  background: var(--color-surface-hover);
}

.act-btn--danger {
  color: var(--color-danger);
}

.act-btn--danger:hover {
  border-color: var(--color-danger);
  background: rgba(220, 38, 38, 0.06);
}

.detail-body {
  padding: 20px;
}

.prop {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  font-size: 13px;
}

.prop-label {
  width: 80px;
  color: var(--color-text-tertiary);
  font-weight: 500;
  flex-shrink: 0;
}

.prop-value {
  color: var(--color-text);
}

.prop-value.overdue {
  color: var(--color-danger);
}

.prop-select {
  padding: 6px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-text);
  font-family: var(--font-body);
  font-size: 13px;
  outline: none;
  transition: border-color var(--transition-fast);
}

.prop-select:focus {
  border-color: var(--color-accent);
}

.level-dots {
  display: flex;
  align-items: center;
  gap: 4px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-border);
  transition: background var(--transition-fast);
}

.dot.filled {
  background: var(--color-accent);
}

.level-num {
  margin-left: 6px;
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.detail-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.detail-tag {
  padding: 3px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  background: color-mix(in srgb, var(--tag-color) 12%, transparent);
  color: var(--tag-color);
}

.desc-section {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--color-border-light);
}

.desc-block {
  margin-top: 8px;
  font-size: 13px;
  color: var(--color-text-secondary);
  line-height: 1.7;
  background: var(--color-bg-base);
  padding: 12px 16px;
  border-radius: var(--radius-md);
}

/* ── Markdown 渲染样式 ── */
.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3),
.markdown-body :deep(h4) {
  font-family: var(--font-heading);
  font-weight: 700;
  color: var(--color-text);
  margin: 14px 0 6px;
  line-height: 1.3;
}
.markdown-body :deep(h1) { font-size: 16px; }
.markdown-body :deep(h2) { font-size: 14px; }
.markdown-body :deep(h3) { font-size: 13px; }

.markdown-body :deep(p) {
  margin: 0 0 8px;
}
.markdown-body :deep(p:last-child) { margin-bottom: 0; }

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  padding-left: 18px;
  margin: 6px 0 8px;
}
.markdown-body :deep(li) { margin-bottom: 3px; }

.markdown-body :deep(code) {
  font-family: 'Menlo', 'Monaco', 'Consolas', monospace;
  font-size: 12px;
  background: var(--color-surface-hover);
  color: var(--color-accent-text);
  padding: 1px 5px;
  border-radius: 4px;
}

.markdown-body :deep(pre) {
  background: var(--color-surface-hover);
  border-radius: var(--radius-sm);
  padding: 10px 12px;
  overflow-x: auto;
  margin: 8px 0;
}
.markdown-body :deep(pre code) {
  background: none;
  padding: 0;
  color: var(--color-text);
  font-size: 12px;
}

.markdown-body :deep(blockquote) {
  border-left: 3px solid var(--color-accent);
  margin: 8px 0;
  padding: 4px 12px;
  color: var(--color-text-tertiary);
}

.markdown-body :deep(a) {
  color: var(--color-accent-text);
  text-decoration: underline;
  text-underline-offset: 2px;
}

.markdown-body :deep(hr) {
  border: none;
  border-top: 1px solid var(--color-border-light);
  margin: 12px 0;
}

.markdown-body :deep(strong) { color: var(--color-text); font-weight: 600; }
.markdown-body :deep(em) { font-style: italic; }

.markdown-body :deep(img) {
  max-width: 100%;
  border-radius: var(--radius-md);
  margin: 8px 0;
  display: block;
  box-shadow: var(--shadow-sm);
}

.detail-badge {
  font-size: 11px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 4px;
  background: var(--color-surface-hover);
  color: var(--color-text-tertiary);
}

.detail-badge.priority-4,
.detail-badge.priority-5 {
  background: rgba(217, 119, 6, 0.1);
  color: var(--color-warning);
}

/* ── 评论区 ── */
.comment-section {
  border-top: 1px solid var(--color-border-light);
  padding: 20px;
}

.comment-section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.comment-section-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.comment-count-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 1px 7px;
  border-radius: 999px;
  background: var(--color-surface-hover);
  color: var(--color-text-tertiary);
}

.comment-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-bottom: 16px;
  max-height: 400px;
  overflow-y: auto;
}

.comment-empty {
  font-size: 13px;
  color: var(--color-text-tertiary);
  text-align: center;
  padding: 12px 0;
}

.comment-item {
  display: flex;
  gap: 10px;
}

.comment-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--color-surface-hover);
  color: var(--color-text-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.comment-body {
  flex: 1;
  min-width: 0;
}

.comment-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.comment-time {
  font-size: 12px;
  color: var(--color-text-tertiary);
  cursor: default;
}

.comment-edited {
  font-size: 11px;
  color: var(--color-text-tertiary);
  font-style: italic;
}

.comment-actions {
  display: flex;
  gap: 4px;
  margin-left: auto;
  opacity: 0;
  pointer-events: none;
  transition: opacity var(--transition-fast);
}

.comment-actions--visible {
  opacity: 1;
  pointer-events: auto;
}

.comment-act-btn {
  font-size: 12px;
  padding: 2px 8px;
  border: 1px solid var(--color-border);
  background: none;
  border-radius: 4px;
  cursor: pointer;
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
}

.comment-act-btn:hover {
  border-color: var(--color-accent);
  color: var(--color-accent-text);
  background: var(--color-accent-subtle);
}

.comment-act-btn--danger:hover {
  border-color: var(--color-danger);
  color: var(--color-danger);
  background: rgba(220, 38, 38, 0.06);
}

.comment-content {
  font-size: 13px;
  color: var(--color-text);
  line-height: 1.6;
}

.comment-edit-area {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.comment-edit-actions {
  display: flex;
  gap: 6px;
  justify-content: flex-end;
}

.comment-save-btn {
  padding: 5px 14px;
  background: var(--color-accent);
  color: white;
  border: none;
  border-radius: var(--radius-pill);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.comment-save-btn:hover { opacity: 0.85; }

.comment-cancel-btn {
  padding: 5px 14px;
  background: none;
  border: 1px solid var(--color-border);
  color: var(--color-text-secondary);
  border-radius: var(--radius-pill);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.comment-cancel-btn:hover {
  background: var(--color-surface-hover);
}

.comment-input-area {
  display: flex;
  flex-direction: column;
  gap: 8px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  overflow: hidden;
  transition: border-color var(--transition-fast);
}

.comment-input-area:focus-within {
  border-color: var(--color-accent);
}

.comment-textarea {
  width: 100%;
  padding: 10px 12px;
  border: none;
  background: var(--color-surface);
  color: var(--color-text);
  font-family: var(--font-body);
  font-size: 13px;
  line-height: 1.6;
  resize: none;
  outline: none;
  box-sizing: border-box;
  field-sizing: content;
  min-height: 72px;
}

.comment-input-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border-top: 1px solid var(--color-border-light);
  background: var(--color-bg-base);
}

.comment-hint {
  font-size: 11px;
  color: var(--color-text-tertiary);
}

.comment-submit-btn {
  padding: 5px 16px;
  background: var(--color-accent);
  color: white;
  border: none;
  border-radius: var(--radius-pill);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.comment-submit-btn:hover:not(:disabled) { opacity: 0.85; }
.comment-submit-btn:disabled { opacity: 0.45; cursor: not-allowed; }

/* --- Confirm Modal --- */
.confirm-modal {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  width: 380px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  box-shadow: var(--shadow-lg);
  animation: scaleIn 0.2s cubic-bezier(0.3, 1.2, 0.2, 1);
  margin: auto;
}

@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

.confirm-body h3 {
  font-family: var(--font-heading);
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 12px 0;
  color: var(--color-text);
}

.confirm-body p {
  font-size: 13px;
  color: var(--color-text-secondary);
  line-height: 1.5;
  margin: 0;
}

.confirm-foot {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn-cancel {
  padding: 8px 20px;
  border: 1px solid var(--color-border);
  background: var(--color-bg-base);
  color: var(--color-text-secondary);
  border-radius: var(--radius-pill);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-cancel:hover {
  color: var(--color-text);
  background: rgba(0,0,0,0.05);
}

.btn-danger {
  padding: 8px 20px;
  border: none;
  background: var(--color-danger);
  color: white;
  border-radius: var(--radius-pill);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-danger:hover {
  background: #DC2626; /* darker red */
}
</style>
