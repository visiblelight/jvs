<template>
  <Teleport to="body">
    <div class="drawer-overlay" @click.self="$emit('close')">
      <div class="drawer-panel" @click.stop>
        <div class="drawer-head">
          <h3>{{ isEdit ? '编辑事项' : '新建事项' }}</h3>
          <button class="close-btn active-scale" @click="$emit('close')">
            <svg viewBox="0 0 16 16" fill="currentColor" width="20" height="20">
              <path d="M3.72 3.72a.75.75 0 011.06 0L8 6.94l3.22-3.22a.75.75 0 111.06 1.06L9.06 8l3.22 3.22a.75.75 0 11-1.06 1.06L8 9.06l-3.22 3.22a.75.75 0 01-1.06-1.06L6.94 8 3.72 4.78a.75.75 0 010-1.06z"/>
            </svg>
          </button>
        </div>

        <form class="drawer-body" @submit.prevent="handleSubmit">
          <div class="field title-field">
            <input v-model="form.title" type="text" placeholder="事项标题..." required class="large-input" />
          </div>
          
          <div class="field">
            <textarea
              ref="descEl"
              v-model="form.description"
              rows="4"
              placeholder="添加详细描述... （支持 Markdown，可 Ctrl+V 粘贴图片）"
              @paste="handlePaste"
            ></textarea>
          </div>

          <div class="field-section">
            <label>优先级</label>
            <div class="segmented-control">
              <button 
                type="button" 
                v-for="(label, idx) in priorities" :key="'p'+idx"
                class="segment-btn active-scale" 
                :class="{ active: form.priority === idx + 1 }"
                @click="form.priority = idx + 1"
              >
                {{ label }}
              </button>
            </div>
          </div>

          <div class="field-section">
            <label>重要程度</label>
            <div class="segmented-control">
              <button 
                type="button" 
                v-for="(label, idx) in importances" :key="'i'+idx"
                class="segment-btn active-scale" 
                :class="{ active: form.importance === idx + 1 }"
                @click="form.importance = idx + 1"
              >
                {{ label }}
              </button>
            </div>
          </div>

          <div class="field-row">
            <div class="field-section">
              <label>分栏分类</label>
              <select v-model="form.category_id" class="minimal-select">
                <option :value="null">收件箱</option>
                <template v-for="cat in flatCategories" :key="cat.id">
                  <option :value="cat.id">{{ cat.prefix }}{{ cat.name }}</option>
                </template>
              </select>
            </div>
            <div class="field-section">
              <label>截止日期</label>
              <input v-model="form.due_date" type="datetime-local" class="minimal-select" />
            </div>
          </div>

          <div class="field-row">
            <div class="field-section">
              <label>🕐 执行时间</label>
              <input v-model="form.scheduled_at" type="datetime-local" class="minimal-select" />
              <span class="field-hint">事项将在此时间点执行</span>
            </div>
            <div class="field-section"></div>
          </div>

          <div class="field-section">
            <label>应用标签</label>
            <div class="tag-picker">
              <label
                v-for="tag in store.tags"
                :key="tag.id"
                class="tag-chip active-scale"
                :class="{ selected: form.tag_ids.includes(tag.id) }"
                :style="form.tag_ids.includes(tag.id) ? { '--chip-color': tag.color } : {}"
              >
                <input type="checkbox" :value="tag.id" v-model="form.tag_ids" hidden />
                <span class="chip-dot" :style="{ background: tag.color }"></span>
                {{ tag.name }}
              </label>
            </div>
          </div>

          <div v-if="isEdit" class="field-section">
            <label>当前状态</label>
            <div class="segmented-control">
              <button type="button" class="segment-btn active-scale" :class="{active: form.status === 'pending'}" @click="form.status='pending'">未完成</button>
              <button type="button" class="segment-btn active-scale" :class="{active: form.status === 'paused'}" @click="form.status='paused'">暂停中</button>
              <button type="button" class="segment-btn active-scale" :class="{active: form.status === 'completed'}" @click="form.status='completed'">已完成</button>
            </div>
          </div>

        </form>

        <div class="drawer-foot">
          <button type="button" class="btn-secondary active-scale" @click="$emit('close')">取消</button>
          <button type="submit" class="btn-primary active-scale" @click="handleSubmit">{{ isEdit ? '保存更改' : '创建任务' }}</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { useTodoStore } from '@/stores/todo'
import { createItem, updateItem } from '@/api/todo'
import { useImagePaste } from '@/composables/useImagePaste'

const descEl = ref(null)
const { handlePaste } = useImagePaste({
  module: 'todo',
  getValue: () => form.description,
  setValue: (val) => { form.description = val },
  getEl: () => descEl.value,
})

const props = defineProps({
  editItem: { type: Object, default: null },
})
const emit = defineEmits(['close', 'saved'])
const store = useTodoStore()
const isEdit = computed(() => !!props.editItem)

const priorities = ['极低', '低', '中等', '高', '极高']
const importances = ['不重要', '一般', '偏重要', '非常重要', '极其重要']

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
  scheduled_at: formatLocalDatetime(props.editItem?.scheduled_at) || '',
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
    scheduled_at: form.scheduled_at ? new Date(form.scheduled_at).toISOString() : null,
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
  gap: 24px;
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
  padding: 16px 20px;
  border: 1px solid transparent;
  background: var(--color-bg-base);
  border-radius: var(--radius-md);
  color: var(--color-text);
  font-size: 14px;
  outline: none;
  resize: none;
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
  padding: 6px 14px;
  background: var(--color-bg-base);
  border: 1px solid transparent;
  border-radius: var(--radius-pill);
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.tag-chip.selected {
  border-color: var(--chip-color);
  background: color-mix(in srgb, var(--chip-color) 12%, transparent);
  color: var(--chip-color);
}

.chip-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
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
.btn-primary:hover {
  background: var(--color-accent-hover);
}

.field-hint {
  font-size: 11px;
  color: var(--color-text-tertiary);
  margin-top: 2px;
}
</style>
