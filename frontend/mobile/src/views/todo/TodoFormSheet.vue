<template>
  <BottomSheet :modelValue="true" @update:modelValue="close"
    :title="isEdit ? '编辑事项' : '新建事项'" maxHeight="88vh">
    <div class="form">
      <TodoDraftStatus :draft="draft" :copied="session.copied" :busy="saving" @discard="discard" />
      <fieldset class="draft-fields" :disabled="saving || draft.completed.value">
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

      </fieldset>
      <button v-if="error && isEdit" type="button" :disabled="saving" @click="saveAsNew">另存为新事项</button>
      <div v-if="error" role="alert" class="form-error">{{ error }}</div>

      <button class="submit-btn" @click="handleSubmit" :disabled="!form.title.trim() || saving || draft.completed.value">
        {{ saving ? '保存中…' : (isEdit ? '保存修改' : '创建事项') }}
      </button>
    </div>
  </BottomSheet>
</template>

<script setup>
import { computed } from 'vue'
import BottomSheet from '@/components/BottomSheet.vue'
import TodoDraftStatus from '@/components/TodoDraftStatus.vue'
import { useTodoStore } from '@/stores/todo'
import { useTodoEditor } from '@/composables/useTodoEditor'
const props = defineProps({ session: { type: Object, required: true } })
const emit = defineEmits(['close', 'saved'])
const todoStore = useTodoStore()
const { form, hasScheduled, isEdit, saving, error, draft, toggleScheduled, close, discard, saveAsNew, handleSubmit } = useTodoEditor(props.session, emit)

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

</script>

<style scoped>
.draft-fields { display: flex; flex-direction: column; gap: 16px; padding: 0; margin: 0; border: 0; min-width: 0; }
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
