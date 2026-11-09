<template>
  <section v-if="drafts.length || error" class="draft-list" aria-label="本机草稿">
    <details :open="!!error">
      <summary>本机草稿（{{ drafts.length }}）</summary>
      <p v-if="error" role="alert">{{ error }}</p>
      <button v-for="draft in drafts" :key="draft.id" type="button" @click="$emit('resume', draft.id)">
        <span>{{ draft.itemId ? '编辑：' : '新建：' }}{{ draft.form.title || '未命名草稿' }}</span>
        <small>{{ formatInstant(draft.savedAt) }} · 继续编辑</small>
      </button>
    </details>
  </section>
</template>
<script setup>
import { formatInstant } from '@/utils/datetime.mjs'
defineProps({ drafts: Array, error: String })
defineEmits(['resume'])
</script>
<style scoped>
.draft-list { padding: 10px 16px; border-bottom: 1px solid var(--color-border); font-size: 13px; }
summary { cursor: pointer; color: var(--color-accent); }
button { display: flex; flex-direction: column; gap: 4px; text-align: left; width: 100%; padding: 10px 0; border: 0; border-bottom: 1px solid var(--color-border); background: transparent; color: inherit; cursor: pointer; }
span { overflow-wrap: anywhere; } small { opacity: .65; } p { color: #b23b3b; }
</style>
