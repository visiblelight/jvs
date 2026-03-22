<template>
  <header class="page-header">
    <button v-if="back" class="back-btn" @click="handleBack">
      <svg viewBox="0 0 24 24" fill="none" width="20" height="20">
        <path d="M15 18l-6-6 6-6" stroke="currentColor" stroke-width="2"
          stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </button>
    <h1 class="header-title">{{ title }}</h1>
    <div class="header-right">
      <slot name="right" />
    </div>
  </header>
</template>

<script setup>
import { useRouter } from 'vue-router'
const props = defineProps({
  title: { type: String, default: '' },
  back: { type: Boolean, default: true },
  backTo: { type: String, default: null },
})
const router = useRouter()
function handleBack() {
  if (props.backTo) router.push(props.backTo)
  else router.back()
}
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  height: 52px;
  padding: 0 16px;
  padding-top: var(--safe-top);
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border-light);
  position: sticky;
  top: 0;
  z-index: 10;
  flex-shrink: 0;
}
.back-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: none;
  color: var(--color-text);
  margin-right: 4px;
  border-radius: var(--radius-sm);
}
.header-title {
  flex: 1;
  font-size: 17px;
  font-weight: 600;
  color: var(--color-text);
  letter-spacing: -0.3px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: 8px;
}
</style>
