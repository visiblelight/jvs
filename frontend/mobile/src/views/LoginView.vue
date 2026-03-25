<template>
  <div class="login-page">
    <div class="login-top">
      <div class="app-logo">
        <svg viewBox="0 0 24 24" fill="none" width="28" height="28">
          <path d="M3 3h8v8H3zM13 3h8v8h-8zM3 13h8v8H3zM17 13a4 4 0 100 8 4 4 0 000-8z"
            fill="currentColor"/>
        </svg>
      </div>
      <h1 class="app-name">JVS</h1>
      <p class="app-desc">移动工作台</p>
    </div>

    <div class="login-card">
      <div class="form-group">
        <label>用户名</label>
        <input
          v-model="form.username"
          type="text"
          placeholder="请输入用户名"
          autocomplete="username"
          @keyup.enter="focusPassword"
          ref="usernameInput"
        />
      </div>
      <div class="form-group">
        <label>密码</label>
        <input
          v-model="form.password"
          type="password"
          placeholder="请输入密码"
          autocomplete="current-password"
          @keyup.enter="handleLogin"
          ref="passwordInput"
        />
      </div>

      <div v-if="error" class="error-msg">{{ error }}</div>

      <button class="login-btn" @click="handleLogin" :disabled="loading || !canSubmit">
        <span v-if="loading" class="btn-loading">
          <span /><span /><span />
        </span>
        <span v-else>登录</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive({ username: '', password: '' })
const error = ref('')
const loading = ref(false)
const passwordInput = ref(null)

const canSubmit = computed(() => form.username && form.password)

function focusPassword() { passwordInput.value?.focus() }

async function handleLogin() {
  if (!canSubmit.value || loading.value) return
  error.value = ''
  loading.value = true
  try {
    await authStore.login(form.username, form.password)
    router.push('/home')
  } catch (e) {
    error.value = e.response?.data?.detail || '登录失败，请检查用户名和密码'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100%;
  background: var(--color-bg);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 24px calc(40px + var(--safe-bottom));
  padding-top: calc(40px + var(--safe-top));
}

.login-top {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 40px;
}

.app-logo {
  width: 72px;
  height: 72px;
  background: var(--color-gradient-accent);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-bottom: 20px;
  box-shadow: var(--shadow-accent);
}

.app-name {
  font-family: 'Syne', sans-serif;
  font-size: 32px;
  font-weight: 800;
  color: var(--color-text);
  letter-spacing: -1.2px;
  margin-bottom: 4px;
}

.app-desc {
  font-size: 15px;
  color: var(--color-text-tertiary);
  font-weight: 500;
}

.login-card {
  width: 100%;
  max-width: 380px;
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  padding: 32px 28px;
  box-shadow: var(--shadow-lg);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.form-group label {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-secondary);
  padding-left: 4px;
}

.form-group input {
  height: 52px;
  padding: 0 16px;
  background: var(--color-bg);
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  font-size: 16px;
  font-weight: 500;
  color: var(--color-text);
  outline: none;
  transition: all var(--transition-fast);
}

.form-group input:focus {
  border-color: var(--color-accent);
  background: var(--color-surface);
  box-shadow: 0 0 0 4px var(--color-accent-subtle);
}

.error-msg {
  font-size: 13px;
  color: var(--color-danger);
  text-align: center;
  font-weight: 500;
}

.login-btn {
  height: 56px;
  background: var(--color-gradient-accent);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: 17px;
  font-weight: 600;
  letter-spacing: 0.5px;
  transition: all var(--transition-spring);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 8px;
  box-shadow: var(--shadow-accent);
}

.login-btn:active:not(:disabled) {
  transform: scale(0.96);
  box-shadow: 0 4px 10px -2px rgba(99, 102, 241, 0.4);
}

.login-btn:disabled { 
  background: var(--color-border);
  color: var(--color-text-tertiary);
  box-shadow: none;
  cursor: not-allowed;
}

.btn-loading {
  display: flex;
  gap: 6px;
}
.btn-loading span {
  width: 8px;
  height: 8px;
  background: white;
  border-radius: 50%;
  animation: bounce 0.6s infinite alternate;
}
.btn-loading span:nth-child(2) { animation-delay: 0.15s; }
.btn-loading span:nth-child(3) { animation-delay: 0.3s; }

@keyframes bounce {
  from { opacity: 0.4; transform: scale(0.8) translateY(0); }
  to   { opacity: 1;   transform: scale(1.1) translateY(-4px); }
}
</style>
