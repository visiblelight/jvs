<template>
  <teleport to="body">
    <transition name="sheet">
      <div v-if="modelValue" class="sheet-overlay" @click.self="$emit('update:modelValue', false)">
        <div class="sheet-panel" :style="{ maxHeight: maxHeight }">
          <div class="sheet-handle" />
          <div class="sheet-header" v-if="title">
            <span class="sheet-title">{{ title }}</span>
            <button class="sheet-close" @click="$emit('update:modelValue', false)">
              <svg viewBox="0 0 24 24" fill="none" width="20" height="20">
                <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2"
                  stroke-linecap="round"/>
              </svg>
            </button>
          </div>
          <div class="sheet-body">
            <slot />
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script setup>
defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: '' },
  maxHeight: { type: String, default: '90vh' },
})
defineEmits(['update:modelValue'])
</script>

<style scoped>
.sheet-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  z-index: 100;
  display: flex;
  align-items: flex-end;
}
.sheet-panel {
  width: 100%;
  background: var(--color-surface);
  border-radius: var(--radius-xl) var(--radius-xl) 0 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding-bottom: var(--safe-bottom);
}
.sheet-handle {
  width: 36px;
  height: 4px;
  background: var(--color-border);
  border-radius: var(--radius-full);
  margin: 12px auto 0;
  flex-shrink: 0;
}
.sheet-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px 12px;
  flex-shrink: 0;
}
.sheet-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--color-text);
  letter-spacing: -0.3px;
}
.sheet-close {
  width: 32px;
  height: 32px;
  border: none;
  background: var(--color-border-light);
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
}
.sheet-body {
  overflow-y: auto;
  flex: 1;
  padding: 0 20px 20px;
}

.sheet-enter-active, .sheet-leave-active {
  transition: opacity 0.25s ease;
}
.sheet-enter-active .sheet-panel,
.sheet-leave-active .sheet-panel {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.sheet-enter-from, .sheet-leave-to { opacity: 0; }
.sheet-enter-from .sheet-panel,
.sheet-leave-to .sheet-panel { transform: translateY(100%); }
</style>
