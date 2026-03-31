<template>
  <BottomSheet :modelValue="modelValue" @update:modelValue="$emit('update:modelValue', $event)"
    :title="item ? '编辑事项' : '新建事项'" maxHeight="88vh">
    <div class="form">
      <div class="form-group">
        <label>标题 *</label>
        <input v-model="form.title" type="text" placeholder="输入事项标题" maxlength="100" />
      </div>

      <div class="form-group">
        <label>描述</label>
        <textarea v-model="form.description" placeholder="添加描述（可选，支持 Markdown）" rows="3" />
      </div>

      <div class="form-row">
        <div class="form-group flex1">
          <label>优先级</label>
          <select v-model="form.priority">
            <option :value="1">极低</option>
            <option :value="2">低</option>
            <option :value="3">中等</option>
            <option :value="4">高</option>
            <option :value="5">极高</option>
          </select>
        </div>
        <div class="form-group flex1">
          <label>重要程度</label>
          <select v-model="form.importance">
            <option :value="1">不重要</option>
            <option :value="2">一般</option>
            <option :value="3">偏重要</option>
            <option :value="4">非常重要</option>
            <option :value="5">极其重要</option>
          </select>
        </div>
      </div>

      <div class="form-group">
        <label>分类</label>
        <select v-model="form.category_id">
          <option :value="null">未分类</option>
          <option v-for="c in flatCategories" :key="c.id" :value="c.id">{{ c.prefix }}{{ c.name }}</option>
        </select>
      </div>

      <div class="form-group">
        <div class="toggle-row">
          <label>指定执行时间</label>
          <button type="button" class="toggle-btn" :class="{ on: hasScheduled }" @click="toggleScheduled">
            <span class="toggle-knob"></span>
          </button>
        </div>
        <template v-if="hasScheduled">
          <input v-model="form.scheduled_at" type="datetime-local" />
          <span class="field-hint">截止时间将自动与执行时间一致</span>
        </template>
        <template v-else>
          <label>截止时间</label>
          <input v-model="form.due_date" type="datetime-local" placeholder="可选" />
          <span class="field-hint">可选，不填则无截止时间</span>
        </template>
      </div>

      <div v-if="todoStore.tags.length" class="form-group">
        <label>标签</label>
        <div class="tag-chips">
          <label
            v-for="tag in todoStore.tags" :key="tag.id"
            class="tag-chip" :class="{ selected: form.tag_ids.includes(tag.id) }"
            :style="form.tag_ids.includes(tag.id) ? { '--chip-color': tag.color } : {}"
          >
            <input type="checkbox" :value="tag.id" v-model="form.tag_ids" hidden />
            <span class="chip-dot" :style="{ background: tag.color }"></span>
            {{ tag.name }}
          </label>
        </div>
      </div>

      <div v-if="error" class="form-error">{{ error }}</div>

      <button class="submit-btn" @click="handleSubmit" :disabled="!form.title.trim() || saving">
        {{ saving ? '保存中…' : (item ? '保存修改' : '创建事项') }}
      </button>
    </div>
  </BottomSheet>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import BottomSheet from '@/components/BottomSheet.vue'
import { useTodoStore } from '@/stores/todo'
import * as api from '@/api/todo'

const props = defineProps({
  modelValue: Boolean,
  item: { type: Object, default: null },
})
const emit = defineEmits(['update:modelValue', 'saved'])

const todoStore = useTodoStore()
const saving = ref(false)
const error = ref('')
const hasScheduled = ref(false)

function formatLocalDatetime(d) {
  if (!d) return ''
  const dt = new Date(d)
  const pad = (n) => String(n).padStart(2, '0')
  return `${dt.getFullYear()}-${pad(dt.getMonth() + 1)}-${pad(dt.getDate())}T${pad(dt.getHours())}:${pad(dt.getMinutes())}`
}

const form = reactive({
  title: '', description: '', priority: 3, importance: 3,
  category_id: null, due_date: '', scheduled_at: '', tag_ids: [],
})

const flatCategories = computed(() => {
  const result = []
  function walk(cats, depth) {
    for (const cat of cats) {
      result.push({ id: cat.id, name: cat.name, prefix: '\u00A0\u00A0'.repeat(depth) })
      if (cat.children) walk(cat.children, depth + 1)
    }
  }
  walk(todoStore.categories, 0)
  return result
})

function toggleScheduled() {
  hasScheduled.value = !hasScheduled.value
  if (!hasScheduled.value) {
    form.scheduled_at = ''
  } else {
    form.scheduled_at = form.due_date || ''
    form.due_date = ''
  }
}

watch(() => props.item, (val) => {
  if (val) {
    form.title = val.title || ''
    form.description = val.description || ''
    form.priority = val.priority || 3
    form.importance = val.importance || 3
    form.category_id = val.category_id || null
    form.due_date = val.scheduled_at ? '' : formatLocalDatetime(val.due_date)
    form.scheduled_at = formatLocalDatetime(val.scheduled_at)
    form.tag_ids = val.tags?.map(t => t.id) || []
    hasScheduled.value = !!val.scheduled_at
  } else {
    form.title = ''
    form.description = ''
    form.priority = 3
    form.importance = 3
    form.category_id = null
    form.due_date = ''
    form.scheduled_at = ''
    form.tag_ids = []
    hasScheduled.value = false
  }
}, { immediate: true })

async function handleSubmit() {
  error.value = ''
  saving.value = true
  try {
    const scheduledIso = hasScheduled.value && form.scheduled_at ? new Date(form.scheduled_at).toISOString() : null
    const payload = {
      title: form.title.trim(),
      description: form.description || null,
      priority: form.priority,
      importance: form.importance,
      category_id: form.category_id || null,
      scheduled_at: scheduledIso,
      due_date: hasScheduled.value ? scheduledIso : (form.due_date ? new Date(form.due_date).toISOString() : null),
      tag_ids: form.tag_ids,
    }
    if (props.item) {
      await api.updateItem(props.item.id, payload)
    } else {
      await api.createItem(payload)
    }
    emit('saved')
    emit('update:modelValue', false)
  } catch (e) {
    error.value = e.response?.data?.detail || '保存失败'
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.form { display: flex; flex-direction: column; gap: 16px; }

.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-group label { font-size: 13px; font-weight: 500; color: var(--color-text-secondary); }

.form-row { display: flex; gap: 12px; }
.flex1 { flex: 1; }

input, textarea, select {
  width: 100%;
  padding: 12px 14px;
  background: var(--color-bg);
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 15px;
  color: var(--color-text);
  outline: none;
  transition: border-color var(--transition-fast);
  font-family: inherit;
}
input:focus, textarea:focus, select:focus { border-color: var(--color-accent); }
textarea { resize: none; line-height: 1.5; }

.toggle-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.toggle-btn {
  display: inline-flex;
  align-items: center;
  width: 40px;
  height: 22px;
  border-radius: var(--radius-full);
  border: none;
  background: var(--color-border);
  cursor: pointer;
  padding: 2px;
  transition: background var(--transition-fast);
  flex-shrink: 0;
}
.toggle-btn.on { background: var(--color-accent); }
.toggle-knob {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: white;
  transition: transform var(--transition-fast);
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}
.toggle-btn.on .toggle-knob { transform: translateX(18px); }

.field-hint {
  font-size: 11px;
  color: var(--color-text-tertiary);
}

.tag-chips { display: flex; flex-wrap: wrap; gap: 8px; }

.tag-chip {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 6px 12px;
  background: var(--color-bg);
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-full);
  font-size: 13px;
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
  width: 7px;
  height: 7px;
  border-radius: 50%;
}

.form-error { font-size: 13px; color: var(--color-danger); }

.submit-btn {
  height: 52px;
  background: var(--color-accent);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: 16px;
  font-weight: 600;
  transition: all var(--transition-fast);
  margin-top: 4px;
}
.submit-btn:active:not(:disabled) { transform: scale(0.98); }
.submit-btn:disabled { opacity: 0.5; }
</style>
