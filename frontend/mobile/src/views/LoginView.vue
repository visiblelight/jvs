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
  width: 64px;
  height: 64px;
  background: var(--color-accent);
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-bottom: 16px;
  box-shadow: 0 8px 24px rgba(79,70,229,0.3);
}

.app-name {
  font-family: 'Syne', sans-serif;
  font-size: 28px;
  font-weight: 800;
  color: var(--color-text);
  letter-spacing: -1px;
  margin-bottom: 4px;
}

.app-desc {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.login-card {
  width: 100%;
  max-width: 360px;
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  padding: 28px 24px;
  box-shadow: var(--shadow-md);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.form-group input {
  height: 48px;
  padding: 0 16px;
  background: var(--color-bg);
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 15px;
  color: var(--color-text);
  outline: none;
  transition: border-color var(--transition-fast);
}

.form-group input:focus {
  border-color: var(--color-accent);
}

.error-msg {
  font-size: 13px;
  color: var(--color-danger);
  text-align: center;
}

.login-btn {
  height: 52px;
  background: var(--color-accent);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0.5px;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 4px;
}

.login-btn:active:not(:disabled) {
  transform: scale(0.98);
  background: var(--color-accent-hover);
}

.login-btn:disabled { opacity: 0.5; }

.btn-loading {
  display: flex;
  gap: 5px;
}
.btn-loading span {
  width: 7px;
  height: 7px;
  background: white;
  border-radius: 50%;
  animation: bounce 0.6s infinite alternate;
}
.btn-loading span:nth-child(2) { animation-delay: 0.15s; }
.btn-loading span:nth-child(3) { animation-delay: 0.3s; }

@keyframes bounce {
  from { opacity: 0.4; transform: translateY(0); }
  to   { opacity: 1;   transform: translateY(-4px); }
}
</style>
