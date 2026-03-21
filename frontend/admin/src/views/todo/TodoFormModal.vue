<template>
  <Teleport to="body">
    <div class="overlay" @click.self="$emit('close')">
      <div class="modal" @click.stop>
        <div class="modal-head">
          <h3>{{ isEdit ? '编辑事项' : '新建事项' }}</h3>
          <button class="close-btn" @click="$emit('close')">
            <svg viewBox="0 0 16 16" fill="currentColor" width="16" height="16"><path d="M3.72 3.72a.75.75 0 011.06 0L8 6.94l3.22-3.22a.75.75 0 111.06 1.06L9.06 8l3.22 3.22a.75.75 0 11-1.06 1.06L8 9.06l-3.22 3.22a.75.75 0 01-1.06-1.06L6.94 8 3.72 4.78a.75.75 0 010-1.06z"/></svg>
          </button>
        </div>
        <form class="modal-body" @submit.prevent="handleSubmit">
          <div class="field">
            <label>标题 <span class="req">*</span></label>
            <input v-model="form.title" type="text" placeholder="输入事项标题" required />
          </div>
          <div class="field">
            <label>描述</label>
            <textarea v-model="form.description" rows="3" placeholder="添加详细描述..."></textarea>
          </div>
          <div class="field-row">
            <div class="field">
              <label>优先级</label>
              <select v-model.number="form.priority">
                <option v-for="n in 5" :key="n" :value="n">{{ n }} 级</option>
              </select>
            </div>
            <div class="field">
              <label>重要程度</label>
              <select v-model.number="form.importance">
                <option v-for="n in 5" :key="n" :value="n">{{ n }} 级</option>
              </select>
            </div>
          </div>
          <div class="field-row">
            <div class="field">
              <label>分类</label>
              <select v-model="form.category_id">
                <option :value="null">无</option>
                <template v-for="cat in flatCategories" :key="cat.id">
                  <option :value="cat.id">{{ cat.prefix }}{{ cat.name }}</option>
                </template>
              </select>
            </div>
            <div class="field">
              <label>截止时间</label>
              <input v-model="form.due_date" type="datetime-local" />
            </div>
          </div>
          <div class="field">
            <label>标签</label>
            <div class="tag-picker">
              <label
                v-for="tag in store.tags"
                :key="tag.id"
                class="tag-chip"
                :class="{ selected: form.tag_ids.includes(tag.id) }"
                :style="form.tag_ids.includes(tag.id) ? { '--chip-color': tag.color } : {}"
              >
                <input type="checkbox" :value="tag.id" v-model="form.tag_ids" hidden />
                <span class="chip-dot" :style="{ background: tag.color }"></span>
                {{ tag.name }}
              </label>
            </div>
          </div>
          <div v-if="isEdit" class="field">
            <label>状态</label>
            <select v-model="form.status">
              <option value="pending">未完成</option>
              <option value="paused">暂停中</option>
              <option value="completed">已完成</option>
            </select>
          </div>
          <div class="modal-foot">
            <button type="button" class="btn-secondary" @click="$emit('close')">取消</button>
            <button type="submit" class="btn-primary">{{ isEdit ? '保存' : '创建' }}</button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, reactive } from 'vue'
import { useTodoStore } from '@/stores/todo'
import { createItem, updateItem } from '@/api/todo'

const props = defineProps({
  editItem: { type: Object, default: null },
})
const emit = defineEmits(['close', 'saved'])
const store = useTodoStore()
const isEdit = computed(() => !!props.editItem)

function formatLocalDatetime(d) {
  if (!d) return ''
  const dt = new Date(d)
  const pad = (n) => String(n).padStart(2, '0')
  return `${dt.getFullYear()}-${pad(dt.getMonth() + 1)}-${pad(dt.getDate())}T${pad(dt.getHours())}:${pad(dt.getMinutes())}`
}

const form = reactive({
  title: props.editItem?.title || '',
  description: props.editItem?.description || '',
  priority: props.editItem?.priority || 3,
  importance: props.editItem?.importance || 3,
  category_id: props.editItem?.category_id || null,
  due_date: formatLocalDatetime(props.editItem?.due_date) || '',
  tag_ids: props.editItem?.tags?.map((t) => t.id) || [],
  status: props.editItem?.status || 'pending',
})

const flatCategories = computed(() => {
  const result = []
  function walk(cats, depth) {
    for (const cat of cats) {
      result.push({ id: cat.id, name: cat.name, prefix: '\u00A0\u00A0'.repeat(depth) })
      if (cat.children) walk(cat.children, depth + 1)
    }
  }
  walk(store.categories, 0)
  return result
})

async function handleSubmit() {
  const payload = {
    title: form.title,
    description: form.description || null,
    priority: form.priority,
    importance: form.importance,
    category_id: form.category_id || null,
    due_date: form.due_date ? new Date(form.due_date).toISOString() : null,
    tag_ids: form.tag_ids,
  }
  if (isEdit.value) {
    payload.status = form.status
    await updateItem(props.editItem.id, payload)
  } else {
    await createItem(payload)
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

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal {
  background: var(--color-surface);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  width: 540px;
  max-height: 85vh;
  overflow-y: auto;
  box-shadow: var(--shadow-overlay);
  animation: slideUp 0.2s ease;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

.modal-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px 0;
}

.modal-head h3 {
  font-family: var(--font-heading);
  font-size: 18px;
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
  padding: 20px 24px 24px;
}

.field {
  margin-bottom: 16px;
}

.field label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary);
  margin-bottom: 5px;
}

.req {
  color: var(--color-danger);
}

.field input,
.field textarea,
.field select {
  width: 100%;
  padding: 9px 12px;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-family: var(--font-body);
  font-size: 13px;
  color: var(--color-text);
  background: var(--color-surface);
  outline: none;
  box-sizing: border-box;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.field input::placeholder,
.field textarea::placeholder {
  color: var(--color-text-tertiary);
}

.field input:focus,
.field textarea:focus,
.field select:focus {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px var(--color-accent-subtle);
}

.field-row {
  display: flex;
  gap: 16px;
}

.field-row .field {
  flex: 1;
}

.tag-picker {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 12px;
  border: 1.5px solid var(--color-border);
  border-radius: 20px;
  font-size: 12px;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.tag-chip.selected {
  border-color: var(--chip-color);
  background: color-mix(in srgb, var(--chip-color) 10%, transparent);
  color: var(--chip-color);
}

.chip-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
}

.modal-foot {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--color-border-light);
}

.btn-secondary {
  padding: 8px 18px;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text-secondary);
  border-radius: var(--radius-sm);
  font-family: var(--font-body);
  font-size: 13px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-secondary:hover {
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

.btn-primary:hover {
  background: var(--color-accent-hover);
}
</style>
