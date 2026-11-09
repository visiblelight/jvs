<template>
  <div class="draft-status" role="status" aria-live="polite">
    <p>{{ draft.status.value }}</p>
    <p v-if="copied">已打开独立副本，原草稿保留。</p>
    <p class="draft-hint">仅保存在当前浏览器；清除站点数据会移除草稿，不跨设备同步。</p>
    <p v-if="draft.storageError.value" class="draft-error">{{ draft.storageError.value }}</p>
    <div class="draft-actions">
      <button type="button" @click="draft.copy">复制全文</button>
      <button type="button" @click="draft.download">下载备份</button>
      <button v-if="draft.storageError.value && !draft.completed.value" type="button" @click="draft.flush">重试保存</button>
      <button v-if="!draft.completed.value" type="button" :disabled="busy" @click="$emit('discard')">丢弃草稿</button>
    </div>
    <textarea v-if="draft.exportText.value" :value="draft.exportText.value" readonly aria-label="可复制的草稿备份" @focus="$event.target.select()" />
  </div>
</template>
<script setup>
defineProps({ draft: Object, copied: Boolean, busy: Boolean })
defineEmits(['discard'])
</script>
<style scoped>
.draft-status { padding: 12px; border: 1px solid var(--color-border); border-radius: 12px; font-size: 12px; line-height: 1.6; }
p { margin: 0 0 5px; }
.draft-hint { opacity: .7; }
.draft-error { color: #b23b3b; }
.draft-actions { display: flex; gap: 12px; flex-wrap: wrap; }
button { cursor: pointer; color: var(--color-accent); background: transparent; border: none; padding: 4px 0; font: inherit; }
textarea { width: 100%; min-height: 100px; margin-top: 8px; }
</style>
