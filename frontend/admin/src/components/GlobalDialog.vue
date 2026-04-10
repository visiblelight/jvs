<template>
  <!-- Toast 通知 -->
  <Teleport to="body">
    <div class="g-toast-wrap" aria-live="polite">
      <TransitionGroup name="g-toast">
        <div
          v-for="t in state.toasts"
          :key="t.id"
          :class="['g-toast', `g-toast--${t.type}`]"
        >
          <span class="g-toast-icon">
            <svg v-if="t.type === 'error'" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><path d="M15 9l-6 6M9 9l6 6"/></svg>
            <svg v-else-if="t.type === 'success'" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><path d="M9 12l2 2 4-4"/></svg>
            <svg v-else viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><path d="M12 8v4m0 4h.01"/></svg>
          </span>
          <span class="g-toast-msg">{{ t.message }}</span>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>

  <!-- 确认弹窗 -->
  <Teleport to="body">
    <Transition name="g-modal">
      <div v-if="state.confirm" class="g-overlay" @click.self="cancel">
        <div class="g-confirm">
          <div class="g-confirm-icon" :class="state.confirm.danger ? 'g-icon--danger' : 'g-icon--warn'">
            <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
          </div>
          <h3 class="g-confirm-title">{{ state.confirm.title }}</h3>
          <p class="g-confirm-msg">{{ state.confirm.message }}</p>
          <div class="g-confirm-actions">
            <button class="g-btn-cancel" @click="cancel">取消</button>
            <button :class="['g-btn-ok', state.confirm.danger ? 'g-btn-danger' : 'g-btn-primary']" @click="ok">确认</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { useDialog } from '@/composables/useDialog'

const { _state: state } = useDialog()

const cancel = () => {
  state.confirm?.resolve(false)
  state.confirm = null
}

const ok = () => {
  state.confirm?.resolve(true)
  state.confirm = null
}
</script>

<style>
/* Toast */
.g-toast-wrap {
  position: fixed;
  top: 24px;
  right: 24px;
  z-index: 99999;
  display: flex;
  flex-direction: column;
  gap: 10px;
  pointer-events: none;
}

.g-toast {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 18px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  box-shadow: 0 8px 32px rgba(0,0,0,0.14);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  max-width: 340px;
  pointer-events: auto;
}

.g-toast--error   { background: rgba(254, 226, 226, 0.95); color: #b91c1c; border: 1px solid #fca5a5; }
.g-toast--success { background: rgba(209, 250, 229, 0.95); color: #065f46; border: 1px solid #6ee7b7; }
.g-toast--info    { background: rgba(219, 234, 254, 0.95); color: #1e40af; border: 1px solid #93c5fd; }

[data-theme="dark"] .g-toast--error   { background: rgba(127, 29, 29, 0.85);  color: #fca5a5; border-color: #7f1d1d; }
[data-theme="dark"] .g-toast--success { background: rgba(6, 78, 59, 0.85);    color: #6ee7b7; border-color: #064e3b; }
[data-theme="dark"] .g-toast--info    { background: rgba(30, 58, 138, 0.85);  color: #93c5fd; border-color: #1e3a8a; }

.g-toast-icon { flex-shrink: 0; display: flex; }
.g-toast-msg  { line-height: 1.4; }

/* Confirm modal */
.g-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 99998;
}

.g-confirm {
  background: var(--color-surface-raised, #fff);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
  padding: 36px 32px 28px;
  max-width: 380px;
  width: 90%;
  text-align: center;
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
}

.g-confirm-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
}

.g-icon--danger { background: rgba(239, 68, 68, 0.1); color: #ef4444; }
.g-icon--warn   { background: rgba(245, 158, 11, 0.1); color: #f59e0b; }

.g-confirm-title {
  font-size: 19px;
  font-weight: 800;
  color: var(--color-text, #111);
  margin: 0 0 10px;
}

.g-confirm-msg {
  font-size: 14px;
  color: var(--color-text-secondary, #6b7280);
  line-height: 1.6;
  margin: 0 0 28px;
}

.g-confirm-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.g-btn-cancel {
  padding: 10px 24px;
  background: transparent;
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 10px;
  font-size: 14px;
  font-weight: 700;
  color: var(--color-text-secondary, #6b7280);
  cursor: pointer;
  transition: all 0.2s;
}
.g-btn-cancel:hover { background: var(--color-surface-hover, #f9fafb); }

.g-btn-ok {
  padding: 10px 24px;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  color: #fff;
  transition: all 0.2s;
}
.g-btn-primary { background: var(--color-accent, #6366f1); box-shadow: 0 4px 12px rgba(99,102,241,0.3); }
.g-btn-primary:hover { filter: brightness(1.1); }
.g-btn-danger  { background: #ef4444; box-shadow: 0 4px 12px rgba(239,68,68,0.3); }
.g-btn-danger:hover { filter: brightness(1.1); }

/* Transitions */
.g-toast-enter-active { transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); }
.g-toast-leave-active { transition: all 0.25s ease; }
.g-toast-enter-from  { opacity: 0; transform: translateX(40px); }
.g-toast-leave-to    { opacity: 0; transform: translateX(40px); }

.g-modal-enter-active { transition: all 0.25s ease; }
.g-modal-leave-active { transition: all 0.2s ease; }
.g-modal-enter-from, .g-modal-leave-to { opacity: 0; }
.g-modal-enter-from .g-confirm { transform: scale(0.92) translateY(8px); }
</style>
