<template>
  <div class="profile-page">
    <header class="page-header">
      <div class="page-eyebrow">账号</div>
      <h1 class="page-title">个人中心</h1>
      <button class="logout-btn" @click="authStore.logout()">退出登录</button>
    </header>
    <div class="profile-content">
      <!-- 基本信息 -->
      <section class="card">
        <h3 class="card-title">基本信息</h3>
        <div class="user-profile-row">
          <div class="avatar-area">
            <UserAvatar :avatar="authStore.user?.avatar" :size="64" :ts="authStore.avatarVersion" />
            <div class="avatar-actions">
              <button class="btn-secondary" @click="triggerFileInput" :disabled="avatarLoading">
                {{ avatarLoading ? '上传中…' : '上传新头像' }}
              </button>
              <button
                v-if="authStore.user?.avatar"
                class="btn-ghost-danger"
                @click="handleDeleteAvatar"
                :disabled="avatarLoading"
              >移除头像</button>
            </div>
            <input
              ref="fileInput"
              type="file"
              accept="image/jpeg,image/png,image/webp,image/gif"
              style="display:none"
              @change="handleFileChange"
            />
            <div v-if="avatarError" class="form-error" style="margin-top:6px">{{ avatarError }}</div>
          </div>
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">用户名</span>
              <span class="info-value">{{ authStore.user?.username }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">创建时间</span>
              <span class="info-value">{{ formatDate(authStore.user?.created_at) }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 修改密码 -->
      <section class="card">
        <h3 class="card-title">修改密码</h3>
        <div class="password-form">
          <div class="form-row">
            <label>旧密码</label>
            <input v-model="pwForm.old_password" type="password" placeholder="输入当前密码" />
          </div>
          <div class="form-row">
            <label>新密码</label>
            <input v-model="pwForm.new_password" type="password" placeholder="至少 6 位" />
          </div>
          <div class="form-row">
            <label>确认密码</label>
            <input v-model="pwConfirm" type="password" placeholder="再次输入新密码" />
          </div>
          <div v-if="pwError" class="form-error">{{ pwError }}</div>
          <div v-if="pwSuccess" class="form-success">{{ pwSuccess }}</div>
          <button class="btn-primary" @click="handleChangePassword" :disabled="!canSubmitPw">修改密码</button>
        </div>
      </section>

      <!-- Access Key 管理 -->
      <section class="card">
        <AccessKeyManager />
      </section>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import request from '@/api/request'
import { uploadAvatar, deleteAvatar } from '@/api/auth'
import AccessKeyManager from './AccessKeyManager.vue'
import UserAvatar from '@/components/UserAvatar.vue'

const authStore = useAuthStore()

const fileInput = ref(null)
const avatarLoading = ref(false)
const avatarError = ref('')

function triggerFileInput() {
  avatarError.value = ''
  fileInput.value?.click()
}

async function handleFileChange(e) {
  const file = e.target.files?.[0]
  if (!file) return
  e.target.value = ''
  avatarError.value = ''
  if (file.size > 2 * 1024 * 1024) {
    avatarError.value = '文件大小不能超过 2MB'
    return
  }
  avatarLoading.value = true
  try {
    await uploadAvatar(file)
    await authStore.fetchUser()
  } catch (err) {
    avatarError.value = err.response?.data?.detail || '上传失败'
  } finally {
    avatarLoading.value = false
  }
}

async function handleDeleteAvatar() {
  avatarError.value = ''
  avatarLoading.value = true
  try {
    await deleteAvatar()
    await authStore.fetchUser()
  } catch (err) {
    avatarError.value = err.response?.data?.detail || '删除失败'
  } finally {
    avatarLoading.value = false
  }
}

const pwForm = reactive({ old_password: '', new_password: '' })
const pwConfirm = ref('')
const pwError = ref('')
const pwSuccess = ref('')

const canSubmitPw = computed(() =>
  pwForm.old_password && pwForm.new_password && pwForm.new_password.length >= 6 && pwForm.new_password === pwConfirm.value
)

async function handleChangePassword() {
  pwError.value = ''
  pwSuccess.value = ''
  if (pwForm.new_password !== pwConfirm.value) {
    pwError.value = '两次输入的密码不一致'
    return
  }
  try {
    await request.put('/admin/auth/password', pwForm)
    pwSuccess.value = '密码修改成功'
    pwForm.old_password = ''
    pwForm.new_password = ''
    pwConfirm.value = ''
  } catch (e) {
    pwError.value = e.response?.data?.detail || '修改失败'
  }
}

function formatDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}
</script>

<style scoped>
.profile-page {
  padding: 36px 40px;
  min-height: 100vh;
  overflow-y: auto;
  background: var(--color-bg);
}

.page-header {
  max-width: 680px;
  margin: 0 auto 36px;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
}

.page-eyebrow {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  color: var(--color-accent-text);
  margin-bottom: 4px;
}

.page-title {
  font-family: var(--font-heading);
  font-size: 36px;
  font-weight: 800;
  color: var(--color-text);
  letter-spacing: -1.5px;
  line-height: 1;
}

.logout-btn {
  padding: 8px 18px;
  background: none;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-pill);
  font-family: var(--font-body);
  font-size: 13px;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
  align-self: center;
}

.logout-btn:hover {
  border-color: var(--color-danger);
  color: var(--color-danger);
}

.profile-content {
  max-width: 680px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  padding: 24px 28px;
}

.card-title {
  font-family: var(--font-heading);
  font-size: 14px;
  font-weight: 700;
  letter-spacing: -0.2px;
  color: var(--color-text);
  margin: 0 0 18px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--color-border-light);
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 12px;
  color: var(--color-text-tertiary);
  font-weight: 500;
}

.info-value {
  font-size: 14px;
  color: var(--color-text);
}

.password-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
  max-width: 400px;
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-row label {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.form-row input {
  padding: 10px 14px;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-md);
  font-family: var(--font-body);
  font-size: 13px;
  color: var(--color-text);
  background: var(--color-surface);
  outline: none;
  transition: border-color var(--transition-fast);
}

.form-row input:focus {
  border-color: var(--color-accent);
}

.form-error {
  font-size: 13px;
  color: var(--color-danger);
}

.form-success {
  font-size: 13px;
  color: var(--color-success);
}

.btn-primary {
  align-self: flex-start;
  padding: 9px 24px;
  background: var(--color-accent);
  color: white;
  border: none;
  border-radius: var(--radius-pill);
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-accent-hover);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.user-profile-row {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

.avatar-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.avatar-actions {
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: center;
}

.btn-secondary {
  padding: 7px 16px;
  background: var(--color-surface);
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-pill);
  font-family: var(--font-body);
  font-size: 12px;
  font-weight: 500;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.btn-secondary:hover:not(:disabled) {
  border-color: var(--color-accent);
  color: var(--color-accent-text);
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-ghost-danger {
  padding: 6px 14px;
  background: none;
  border: none;
  font-family: var(--font-body);
  font-size: 12px;
  color: var(--color-text-tertiary);
  cursor: pointer;
  transition: color var(--transition-fast);
}

.btn-ghost-danger:hover:not(:disabled) {
  color: var(--color-danger);
}

.btn-ghost-danger:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
