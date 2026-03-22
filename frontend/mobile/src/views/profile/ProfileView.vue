<template>
  <div class="profile-page">
    <div class="profile-header">
      <UserAvatar
        :avatar="authStore.user?.avatar"
        :size="72"
        :ts="authStore.avatarVersion"
      />
      <h2 class="profile-name">{{ authStore.user?.username }}</h2>
      <p class="profile-since">加入于 {{ formatDate(authStore.user?.created_at) }}</p>
    </div>

    <div class="section">
      <div class="section-title">账号设置</div>
      <div class="card">
        <div class="card-item" @click="showPwSheet = true">
          <div class="item-icon item-icon--purple">
            <svg viewBox="0 0 24 24" fill="none" width="16" height="16">
              <rect x="5" y="11" width="14" height="10" rx="2" stroke="white" stroke-width="1.8"/>
              <path d="M8 11V7a4 4 0 018 0v4" stroke="white" stroke-width="1.8" stroke-linecap="round"/>
            </svg>
          </div>
          <span class="item-label">修改密码</span>
          <svg class="item-arrow" viewBox="0 0 24 24" fill="none" width="16" height="16">
            <path d="M9 18l6-6-6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>

        <div class="card-item" @click="themeStore.toggle()">
          <div class="item-icon item-icon--blue">
            <svg viewBox="0 0 24 24" fill="none" width="16" height="16">
              <path v-if="themeStore.theme === 'light'"
                d="M21 12.79A9 9 0 1111.21 3a7 7 0 009.79 9.79z"
                stroke="white" stroke-width="1.8" stroke-linecap="round"/>
              <path v-else
                d="M12 3v1m0 16v1M4.22 4.22l.71.71m12.73 12.73l.71.71M3 12H2m20 0h-1M4.22 19.78l.71-.71M18.36 5.64l.71-.71M16 12a4 4 0 11-8 0 4 4 0 018 0z"
                stroke="white" stroke-width="1.8" stroke-linecap="round"/>
            </svg>
          </div>
          <span class="item-label">{{ themeStore.theme === 'light' ? '切换夜间模式' : '切换日间模式' }}</span>
          <svg class="item-arrow" viewBox="0 0 24 24" fill="none" width="16" height="16">
            <path d="M9 18l6-6-6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>
      </div>
    </div>

    <div class="section">
      <div class="card">
        <div class="card-item card-item--danger" @click="authStore.logout()">
          <div class="item-icon item-icon--red">
            <svg viewBox="0 0 24 24" fill="none" width="16" height="16">
              <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4M16 17l5-5-5-5M21 12H9"
                stroke="white" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <span class="item-label">退出登录</span>
        </div>
      </div>
    </div>

    <!-- 修改密码 Sheet -->
    <BottomSheet v-model="showPwSheet" title="修改密码">
      <div class="pw-form">
        <div class="form-group">
          <label>旧密码</label>
          <input v-model="pw.old_password" type="password" placeholder="输入当前密码" />
        </div>
        <div class="form-group">
          <label>新密码</label>
          <input v-model="pw.new_password" type="password" placeholder="至少 6 位" />
        </div>
        <div class="form-group">
          <label>确认新密码</label>
          <input v-model="pw.confirm" type="password" placeholder="再次输入新密码" />
        </div>
        <div v-if="pwError" class="form-error">{{ pwError }}</div>
        <div v-if="pwSuccess" class="form-success">{{ pwSuccess }}</div>
        <button class="submit-btn" @click="handleChangePw" :disabled="!canSubmitPw || pwSaving">
          {{ pwSaving ? '保存中…' : '确认修改' }}
        </button>
      </div>
    </BottomSheet>
  </div>
</template>

<script setup>
import { reactive, ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { changePassword } from '@/api/auth'
import UserAvatar from '@/components/UserAvatar.vue'
import BottomSheet from '@/components/BottomSheet.vue'

const authStore = useAuthStore()
const themeStore = useThemeStore()

const showPwSheet = ref(false)
const pw = reactive({ old_password: '', new_password: '', confirm: '' })
const pwError = ref('')
const pwSuccess = ref('')
const pwSaving = ref(false)

const canSubmitPw = computed(() =>
  pw.old_password && pw.new_password.length >= 6 && pw.new_password === pw.confirm
)

async function handleChangePw() {
  pwError.value = ''; pwSuccess.value = ''
  pwSaving.value = true
  try {
    await changePassword({ old_password: pw.old_password, new_password: pw.new_password })
    pwSuccess.value = '密码修改成功'
    pw.old_password = ''; pw.new_password = ''; pw.confirm = ''
  } catch (e) {
    pwError.value = e.response?.data?.detail || '修改失败'
  } finally {
    pwSaving.value = false
  }
}

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}
</script>

<style scoped>
.profile-page {
  height: 100%;
  overflow-y: auto;
  background: var(--color-bg);
  padding-top: var(--safe-top);
  padding-bottom: calc(24px + var(--safe-bottom));
}

.profile-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 24px 32px;
  gap: 10px;
}

.profile-name {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-text);
  letter-spacing: -0.5px;
}

.profile-since {
  font-size: 13px;
  color: var(--color-text-tertiary);
}

.section { padding: 0 16px 12px; }

.section-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 0 4px 8px;
}

.card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.card-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  border-bottom: 1px solid var(--color-border-light);
  cursor: pointer;
  transition: background var(--transition-fast);
}
.card-item:last-child { border-bottom: none; }
.card-item:active { background: var(--color-border-light); }
.card-item--danger .item-label { color: var(--color-danger); }

.item-icon {
  width: 32px; height: 32px;
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.item-icon--purple { background: var(--color-accent); }
.item-icon--blue   { background: #0EA5E9; }
.item-icon--red    { background: var(--color-danger); }

.item-label { flex: 1; font-size: 15px; color: var(--color-text); }

.item-arrow { color: var(--color-text-tertiary); flex-shrink: 0; }

/* Password form */
.pw-form { display: flex; flex-direction: column; gap: 16px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-group label { font-size: 13px; font-weight: 500; color: var(--color-text-secondary); }
.form-group input {
  height: 48px; padding: 0 14px;
  background: var(--color-bg);
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 15px; color: var(--color-text);
  outline: none; font-family: inherit;
  transition: border-color var(--transition-fast);
}
.form-group input:focus { border-color: var(--color-accent); }
.form-error { font-size: 13px; color: var(--color-danger); }
.form-success { font-size: 13px; color: var(--color-success); }
.submit-btn {
  height: 52px; background: var(--color-accent); color: white;
  border: none; border-radius: var(--radius-md);
  font-size: 16px; font-weight: 600; margin-top: 4px;
  transition: all var(--transition-fast);
}
.submit-btn:active:not(:disabled) { transform: scale(0.98); }
.submit-btn:disabled { opacity: 0.5; }
</style>
