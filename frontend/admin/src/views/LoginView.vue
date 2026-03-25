<template>
  <div class="login-page">
    <!-- Animated mesh background -->
    <div class="mesh-bg">
      <div class="mesh-orb mesh-orb--1"></div>
      <div class="mesh-orb mesh-orb--2"></div>
      <div class="mesh-orb mesh-orb--3"></div>
    </div>

    <!-- Grid overlay -->
    <div class="grid-overlay"></div>

    <div class="login-container">
      <!-- Left: brand column -->
      <div class="brand-col">
        <div class="brand-lockup">
          <div class="brand-icon">
            <svg viewBox="0 0 32 32" width="28" height="28">
              <path d="M20 7 L20 22 C20 28 10 28 10 21"
                    fill="none" stroke="currentColor" stroke-width="5.5"
                    stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h1 class="brand-name">JVS</h1>
          <p class="brand-tagline">Management Console</p>
        </div>
        <div class="brand-footer">
          <span class="version-tag">v0.1</span>
        </div>
      </div>

      <!-- Right: form column -->
      <div class="form-col">
        <div class="form-inner">
          <div class="form-header">
            <h2 class="form-title">欢迎回来</h2>
            <p class="form-subtitle">请登录以继续</p>
          </div>

          <form @submit.prevent="handleLogin">
            <div class="field" :class="{ 'field--focused': focusedField === 'username', 'field--filled': username }">
              <label>账号</label>
              <input
                v-model="username"
                type="text"
                placeholder="输入用户名"
                autocomplete="username"
                @focus="focusedField = 'username'"
                @blur="focusedField = ''"
              />
              <div class="field-line"></div>
            </div>

            <div class="field" :class="{ 'field--focused': focusedField === 'password', 'field--filled': password }">
              <label>密码</label>
              <input
                v-model="password"
                type="password"
                placeholder="输入密码"
                autocomplete="current-password"
                @focus="focusedField = 'password'"
                @blur="focusedField = ''"
              />
              <div class="field-line"></div>
            </div>

            <p v-if="errorMsg" class="error-msg">
              <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14"><path d="M8 1a7 7 0 100 14A7 7 0 008 1zm-.75 3.5a.75.75 0 011.5 0v4a.75.75 0 01-1.5 0v-4zm.75 8a1 1 0 110-2 1 1 0 010 2z"/></svg>
              {{ errorMsg }}
            </p>

            <button type="submit" class="login-btn" :disabled="loading">
              <span v-if="!loading">登录</span>
              <span v-else class="btn-loading">
                <span class="dot"></span><span class="dot"></span><span class="dot"></span>
              </span>
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const errorMsg = ref('')
const loading = ref(false)
const focusedField = ref('')

async function handleLogin() {
  errorMsg.value = ''
  if (!username.value || !password.value) {
    errorMsg.value = '请输入账号和密码'
    return
  }
  loading.value = true
  try {
    await authStore.login(username.value, password.value)
    router.push('/dashboard')
  } catch (e) {
    errorMsg.value = e.response?.data?.detail || '登录失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg);
  position: relative;
  overflow: hidden;
}

/* Mesh gradient background */
.mesh-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.mesh-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.45;
}

[data-theme="dark"] .mesh-orb { opacity: 0.25; }

.mesh-orb--1 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, #57C74A 0%, transparent 70%);
  top: -150px;
  left: -100px;
  animation: drift1 14s ease-in-out infinite alternate;
}

.mesh-orb--2 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, #2AAF25 0%, transparent 70%);
  bottom: -100px;
  right: -80px;
  animation: drift2 18s ease-in-out infinite alternate;
}

.mesh-orb--3 {
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, #09ADC3 0%, transparent 70%);
  top: 50%;
  left: 40%;
  animation: drift3 10s ease-in-out infinite alternate;
}

@keyframes drift1 {
  from { transform: translate(0, 0) scale(1); }
  to { transform: translate(60px, 40px) scale(1.1); }
}

@keyframes drift2 {
  from { transform: translate(0, 0) scale(1); }
  to { transform: translate(-40px, -60px) scale(1.15); }
}

@keyframes drift3 {
  from { transform: translate(0, 0) scale(1); }
  to { transform: translate(30px, -50px) scale(0.9); }
}

/* Grid overlay */
.grid-overlay {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background-image:
    linear-gradient(var(--color-border-light) 1px, transparent 1px),
    linear-gradient(90deg, var(--color-border-light) 1px, transparent 1px);
  background-size: 48px 48px;
  opacity: 0.5;
  mask-image: radial-gradient(ellipse 70% 70% at 50% 50%, black 30%, transparent 100%);
}

/* Container */
.login-container {
  display: flex;
  width: 820px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  overflow: hidden;
  position: relative;
  z-index: 1;
  box-shadow: var(--shadow-lg);
  animation: panelEnter 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;
}

@keyframes panelEnter {
  from { opacity: 0; transform: scale(0.97) translateY(16px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

/* Brand column */
.brand-col {
  width: 340px;
  flex-shrink: 0;
  background: var(--color-accent);
  padding: 48px 40px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  position: relative;
  overflow: hidden;
}

.brand-col::after {
  content: '';
  position: absolute;
  right: -60px;
  top: -60px;
  width: 240px;
  height: 240px;
  background: rgba(255, 255, 255, 0.07);
  border-radius: 50%;
}

.brand-col::before {
  content: '';
  position: absolute;
  left: -40px;
  bottom: -80px;
  width: 280px;
  height: 280px;
  background: rgba(0, 0, 0, 0.08);
  border-radius: 50%;
}

.brand-lockup {
  position: relative;
  z-index: 1;
}

.brand-icon {
  width: 54px;
  height: 54px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-bottom: 24px;
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.brand-name {
  font-family: var(--font-heading);
  font-size: 48px;
  font-weight: 800;
  color: white;
  letter-spacing: -2px;
  line-height: 1;
  margin-bottom: 8px;
}

.brand-tagline {
  font-size: 12px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.65);
  letter-spacing: 2px;
  text-transform: uppercase;
}

.brand-footer {
  position: relative;
  z-index: 1;
}

.version-tag {
  font-size: 11px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.4);
  letter-spacing: 1.5px;
  text-transform: uppercase;
}

/* Form column */
.form-col {
  flex: 1;
  padding: 48px 40px;
  display: flex;
  align-items: center;
}

.form-inner {
  width: 100%;
  max-width: 320px;
}

.form-header {
  margin-bottom: 36px;
}

.form-title {
  font-family: var(--font-heading);
  font-size: 26px;
  font-weight: 700;
  color: var(--color-text);
  letter-spacing: -0.5px;
  margin-bottom: 4px;
}

.form-subtitle {
  font-size: 14px;
  color: var(--color-text-tertiary);
}

/* Fields */
.field {
  margin-bottom: 28px;
  position: relative;
}

.field label {
  display: block;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: var(--color-text-tertiary);
  margin-bottom: 8px;
  transition: color var(--transition-fast);
}

.field--focused label,
.field--filled label {
  color: var(--color-accent-text);
}

.field input {
  width: 100%;
  border: none;
  border-bottom: 1.5px solid var(--color-border);
  background: none;
  padding: 10px 0;
  font-family: var(--font-body);
  font-size: 15px;
  color: var(--color-text);
  outline: none;
  transition: border-color var(--transition-fast);
}

.field input::placeholder {
  color: var(--color-text-tertiary);
  font-size: 14px;
}

.field-line {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 2px;
  background: var(--color-accent);
  transition: width var(--transition-base);
  border-radius: 1px;
}

.field--focused .field-line {
  width: 100%;
}

.error-msg {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--color-danger);
  margin: -12px 0 20px;
}

.login-btn {
  width: 100%;
  height: 48px;
  background: var(--color-accent);
  color: white;
  border: none;
  border-radius: var(--radius-pill);
  font-family: var(--font-heading);
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 0.5px;
  cursor: pointer;
  transition: all var(--transition-fast);
  margin-top: 8px;
  position: relative;
  overflow: hidden;
}

.login-btn::after {
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0);
  transition: background var(--transition-fast);
}

.login-btn:hover:not(:disabled)::after {
  background: rgba(255, 255, 255, 0.08);
}

.login-btn:active:not(:disabled) {
  transform: scale(0.99);
}

.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Loading dots */
.btn-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
}

.dot {
  width: 6px;
  height: 6px;
  background: white;
  border-radius: 50%;
  animation: dotBounce 0.9s ease-in-out infinite;
}

.dot:nth-child(2) { animation-delay: 0.15s; }
.dot:nth-child(3) { animation-delay: 0.3s; }

@keyframes dotBounce {
  0%, 100% { transform: translateY(0); opacity: 0.4; }
  50% { transform: translateY(-5px); opacity: 1; }
}
</style>
