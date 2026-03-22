<template>
  <BottomSheet :modelValue="modelValue" @update:modelValue="$emit('update:modelValue', $event)"
    :title="item ? '编辑待办' : '新建待办'" maxHeight="88vh">
    <div class="form">
      <div class="form-group">
        <label>标题 *</label>
        <input v-model="form.title" type="text" placeholder="输入待办标题" maxlength="100" />
      </div>

      <div class="form-group">
        <label>备注</label>
        <textarea v-model="form.description" placeholder="添加备注（可选）" rows="3" />
      </div>

      <div class="form-row">
        <div class="form-group flex1">
          <label>优先级</label>
          <select v-model="form.priority">
            <option value="low">低</option>
            <option value="medium">中</option>
            <option value="high">高</option>
          </select>
        </div>
        <div class="form-group flex1">
          <label>分类</label>
          <select v-model="form.category_id">
            <option :value="null">无</option>
            <option v-for="c in todoStore.categories" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
        </div>
      </div>

      <div class="form-group">
        <label>截止日期</label>
        <input v-model="form.due_date" type="date" />
      </div>

      <div v-if="error" class="form-error">{{ error }}</div>

      <button class="submit-btn" @click="handleSubmit" :disabled="!form.title.trim() || saving">
        {{ saving ? '保存中…' : (item ? '保存修改' : '创建待办') }}
      </button>
    </div>
  </BottomSheet>
</template>

<script setup>
import { reactive, ref, watch } from 'vue'
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

const form = reactive({ title: '', description: '', priority: 'medium', category_id: null, due_date: '' })

watch(() => props.item, (val) => {
  if (val) {
    form.title = val.title || ''
    form.description = val.description || ''
    form.priority = val.priority || 'medium'
    form.category_id = val.category_id || null
    form.due_date = val.due_date ? val.due_date.substring(0, 10) : ''
  } else {
    form.title = ''
    form.description = ''
    form.priority = 'medium'
    form.category_id = null
    form.due_date = ''
  }
}, { immediate: true })

async function handleSubmit() {
  error.value = ''
  saving.value = true
  try {
    const payload = {
      title: form.title.trim(),
      description: form.description || null,
      priority: form.priority,
      category_id: form.category_id || null,
      due_date: form.due_date || null,
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
