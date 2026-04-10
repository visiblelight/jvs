<template>
  <div class="users-page">
    <header class="page-header">
      <div class="page-eyebrow">系统</div>
      <h1 class="page-title">用户管理</h1>
      <button class="btn-create" @click="openCreateModal">
        <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14"><path d="M8 2a.75.75 0 01.75.75v4.5h4.5a.75.75 0 010 1.5h-4.5v4.5a.75.75 0 01-1.5 0v-4.5h-4.5a.75.75 0 010-1.5h4.5v-4.5A.75.75 0 018 2z"/></svg>
        新建用户
      </button>
    </header>

    <div class="page-content">
      <div v-if="loading" class="empty">加载中…</div>
      <div v-else-if="users.length === 0" class="empty">暂无用户</div>
      <div v-else class="user-list">
        <div v-for="u in users" :key="u.id" class="user-row" :class="{ 'user-row--disabled': !u.is_active }">
          <UserAvatar :avatar="u.avatar" :size="40" :ts="avatarTs" />
          <div class="user-info">
            <div class="user-name-row">
              <span class="user-name">{{ u.username }}</span>
              <span v-if="u.is_superuser" class="tag tag--super">超管</span>
              <span v-if="!u.is_active" class="tag tag--muted">已禁用</span>
            </div>
            <div class="user-meta">
              <span v-if="u.is_superuser">全部板块权限</span>
              <span v-else>{{ u.module_count }} 个板块权限</span>
              <span class="meta-sep">·</span>
              <span>ID {{ u.id }}</span>
            </div>
          </div>
          <div class="user-actions">
            <button class="link-btn" @click="openEditModal(u)">编辑</button>
            <button v-if="!u.is_superuser" class="link-btn" @click="openModulesModal(u)">板块</button>
            <label class="switch" :title="u.is_active ? '禁用' : '启用'">
              <input
                type="checkbox"
                :checked="u.is_active"
                :disabled="u.id === authStore.user?.id"
                @change="toggleActive(u)"
              />
              <span class="slider"></span>
            </label>
          </div>
        </div>
      </div>
    </div>

    <!-- 新建 / 编辑 弹窗 -->
    <Teleport to="body">
      <div v-if="showFormModal" class="overlay" @click.self="closeFormModal">
        <div class="modal" @click.stop>
          <div class="modal-head">
            <h3>{{ editingUser ? '编辑用户' : '新建用户' }}</h3>
            <button class="close-btn" @click="closeFormModal">
              <svg viewBox="0 0 16 16" fill="currentColor" width="16" height="16"><path d="M3.72 3.72a.75.75 0 011.06 0L8 6.94l3.22-3.22a.75.75 0 111.06 1.06L9.06 8l3.22 3.22a.75.75 0 11-1.06 1.06L8 9.06l-3.22 3.22a.75.75 0 01-1.06-1.06L6.94 8 3.72 4.78a.75.75 0 010-1.06z"/></svg>
            </button>
          </div>
          <div class="modal-body">
            <div class="form-row">
              <label>用户名</label>
              <input v-model="form.username" placeholder="登录用户名" />
            </div>
            <div class="form-row">
              <label>{{ editingUser ? '重置密码（留空不修改）' : '密码' }}</label>
              <input v-model="form.password" type="password" placeholder="至少 6 位" />
            </div>
            <div class="form-row">
              <label class="inline-check">
                <input
                  type="checkbox"
                  v-model="form.is_superuser"
                  :disabled="editingUser && editingUser.id === authStore.user?.id"
                />
                <span>超级管理员</span>
              </label>
              <div class="form-hint">超级管理员拥有全部板块权限，无需单独配置</div>
            </div>
            <div v-if="!form.is_superuser" class="form-row">
              <label>板块权限</label>
              <div class="module-checks">
                <label v-for="m in availableModules" :key="m.key" class="module-check">
                  <input type="checkbox" :value="m.key" v-model="form.modules" />
                  <span>{{ m.label }}</span>
                </label>
              </div>
            </div>
            <div v-if="formError" class="form-error">{{ formError }}</div>
          </div>
          <div class="modal-footer">
            <button class="btn-cancel" @click="closeFormModal">取消</button>
            <button class="btn-primary" @click="submitForm" :disabled="submitting || !canSubmit">
              {{ submitting ? '保存中…' : '保存' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 板块权限 弹窗 -->
    <Teleport to="body">
      <div v-if="modulesModalUser" class="overlay" @click.self="modulesModalUser = null">
        <div class="modal" @click.stop>
          <div class="modal-head">
            <h3>板块权限 — {{ modulesModalUser.username }}</h3>
            <button class="close-btn" @click="modulesModalUser = null">
              <svg viewBox="0 0 16 16" fill="currentColor" width="16" height="16"><path d="M3.72 3.72a.75.75 0 011.06 0L8 6.94l3.22-3.22a.75.75 0 111.06 1.06L9.06 8l3.22 3.22a.75.75 0 11-1.06 1.06L8 9.06l-3.22 3.22a.75.75 0 01-1.06-1.06L6.94 8 3.72 4.78a.75.75 0 010-1.06z"/></svg>
            </button>
          </div>
          <div class="modal-body">
            <div class="module-checks">
              <label v-for="m in availableModules" :key="m.key" class="module-check">
                <input type="checkbox" :value="m.key" v-model="modulesDraft" />
                <span>{{ m.label }}</span>
              </label>
            </div>
            <div v-if="modulesError" class="form-error">{{ modulesError }}</div>
          </div>
          <div class="modal-footer">
            <button class="btn-cancel" @click="modulesModalUser = null">取消</button>
            <button class="btn-primary" @click="saveModules" :disabled="submitting">
              {{ submitting ? '保存中…' : '保存' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useDialog } from '@/composables/useDialog'
const { toast } = useDialog()
import * as api from '@/api/users'
import { useAuthStore } from '@/stores/auth'
import UserAvatar from '@/components/UserAvatar.vue'

const authStore = useAuthStore()

const users = ref([])
const availableModules = ref([])
const loading = ref(true)
const submitting = ref(false)
const avatarTs = ref(Date.now())

const showFormModal = ref(false)
const editingUser = ref(null)
const form = reactive({
  username: '',
  password: '',
  is_superuser: false,
  is_active: true,
  modules: [],
})
const formError = ref('')

const modulesModalUser = ref(null)
const modulesDraft = ref([])
const modulesError = ref('')

const canSubmit = computed(() => {
  if (!form.username.trim()) return false
  if (!editingUser.value && !form.password) return false
  if (form.password && form.password.length < 6) return false
  return true
})

async function fetchUsers() {
  loading.value = true
  try {
    const { data } = await api.listUsers()
    users.value = data
  } finally {
    loading.value = false
  }
}

async function fetchModules() {
  const { data } = await api.listModules()
  availableModules.value = data
}

onMounted(() => {
  fetchUsers()
  fetchModules()
})

function resetForm() {
  form.username = ''
  form.password = ''
  form.is_superuser = false
  form.is_active = true
  form.modules = []
  formError.value = ''
}

function openCreateModal() {
  editingUser.value = null
  resetForm()
  showFormModal.value = true
}

function openEditModal(u) {
  editingUser.value = u
  form.username = u.username
  form.password = ''
  form.is_superuser = u.is_superuser
  form.is_active = u.is_active
  form.modules = []
  formError.value = ''
  showFormModal.value = true
}

function closeFormModal() {
  showFormModal.value = false
  editingUser.value = null
  resetForm()
}

async function submitForm() {
  formError.value = ''
  submitting.value = true
  try {
    if (editingUser.value) {
      const payload = {
        username: form.username.trim(),
        is_superuser: form.is_superuser,
      }
      if (form.password) payload.password = form.password
      await api.updateUser(editingUser.value.id, payload)
    } else {
      const payload = {
        username: form.username.trim(),
        password: form.password,
        is_active: true,
        is_superuser: form.is_superuser,
        modules: form.is_superuser ? [] : form.modules,
      }
      await api.createUser(payload)
    }
    closeFormModal()
    await fetchUsers()
  } catch (e) {
    formError.value = e?.response?.data?.detail || '保存失败'
  } finally {
    submitting.value = false
  }
}

async function toggleActive(u) {
  try {
    await api.updateUser(u.id, { is_active: !u.is_active })
    await fetchUsers()
  } catch (e) {
    toast(e?.response?.data?.detail || '操作失败')
  }
}

async function openModulesModal(u) {
  modulesError.value = ''
  try {
    const { data } = await api.getUser(u.id)
    modulesDraft.value = [...(data.modules || [])]
    modulesModalUser.value = data
  } catch (e) {
    toast(e?.response?.data?.detail || '获取用户详情失败')
  }
}

async function saveModules() {
  if (!modulesModalUser.value) return
  submitting.value = true
  modulesError.value = ''
  try {
    await api.setUserModules(modulesModalUser.value.id, modulesDraft.value)
    modulesModalUser.value = null
    await fetchUsers()
  } catch (e) {
    modulesError.value = e?.response?.data?.detail || '保存失败'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.users-page {
  padding: 32px 40px;
  max-width: 960px;
  margin: 0 auto;
}

.page-header {
  position: relative;
  margin-bottom: 28px;
}

.page-eyebrow {
  font-size: 11px;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--color-text-tertiary);
  margin-bottom: 6px;
  font-weight: 600;
}

.page-title {
  font-family: var(--font-heading);
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.6px;
  color: var(--color-text);
  margin: 0;
}

.btn-create {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 9px 20px;
  background: var(--color-accent);
  color: white;
  border: none;
  border-radius: var(--radius-pill);
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background var(--transition-fast);
}

.btn-create:hover { background: var(--color-accent-hover); }

.page-content {
  background: var(--color-surface);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  padding: 12px 20px;
}

.empty {
  text-align: center;
  padding: 48px 0;
  color: var(--color-text-tertiary);
  font-size: 13px;
}

.user-list {
  display: flex;
  flex-direction: column;
}

.user-row {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 4px;
  border-bottom: 1px solid var(--color-border-light);
}

.user-row:last-child { border-bottom: none; }

.user-row--disabled { opacity: 0.55; }

.user-info {
  flex: 1;
  min-width: 0;
}

.user-name-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
}

.tag {
  font-size: 10px;
  font-weight: 600;
  padding: 2px 7px;
  border-radius: 4px;
  letter-spacing: 0.3px;
}

.tag--super {
  background: var(--color-accent-subtle);
  color: var(--color-accent-text);
}

.tag--muted {
  background: var(--color-surface-hover);
  color: var(--color-text-tertiary);
}

.user-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--color-text-tertiary);
  margin-top: 3px;
}

.meta-sep { opacity: 0.5; }

.user-actions {
  display: flex;
  align-items: center;
  gap: 14px;
}

.link-btn {
  border: none;
  background: none;
  font-family: var(--font-body);
  font-size: 12px;
  color: var(--color-accent-text);
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.link-btn:hover { opacity: 0.75; }

.switch {
  position: relative;
  width: 36px;
  height: 20px;
  display: inline-block;
}

.switch input { opacity: 0; width: 0; height: 0; }

.slider {
  position: absolute;
  inset: 0;
  background: var(--color-border);
  border-radius: 10px;
  cursor: pointer;
  transition: background var(--transition-fast);
}

.slider::before {
  content: '';
  position: absolute;
  width: 16px;
  height: 16px;
  left: 2px;
  top: 2px;
  background: white;
  border-radius: 50%;
  transition: transform var(--transition-fast);
}

.switch input:checked + .slider { background: var(--color-accent); }
.switch input:checked + .slider::before { transform: translateX(16px); }
.switch input:disabled + .slider { cursor: not-allowed; opacity: 0.6; }

/* Modal */
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  animation: fadeIn 0.15s ease;
}

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.modal {
  background: var(--color-surface);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-xl);
  width: 480px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: var(--shadow-overlay);
  animation: slideUp 0.2s ease;
}

@keyframes slideUp { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }

.modal-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--color-border-light);
}

.modal-head h3 {
  font-family: var(--font-heading);
  font-size: 17px;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.close-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: none;
  color: var(--color-text-tertiary);
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.close-btn:hover {
  background: var(--color-surface-hover);
  color: var(--color-text);
}

.modal-body { padding: 20px 24px; }

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 16px 24px;
  border-top: 1px solid var(--color-border-light);
}

.form-row { margin-bottom: 16px; }

.form-row > label:not(.inline-check) {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary);
  margin-bottom: 6px;
}

.form-row input[type="text"],
.form-row input[type="password"],
.form-row input:not([type]) {
  width: 100%;
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

.form-row input:focus { border-color: var(--color-accent); }

.form-hint {
  font-size: 11px;
  color: var(--color-text-tertiary);
  margin-top: 4px;
}

.inline-check {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--color-text);
  cursor: pointer;
  margin: 0;
}

.inline-check input { accent-color: var(--color-accent); width: 16px; height: 16px; }

.module-checks {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.module-check {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--color-text);
  cursor: pointer;
}

.module-check input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: var(--color-accent);
}

.form-error {
  font-size: 13px;
  color: var(--color-danger);
  margin-top: 4px;
}

.btn-cancel {
  padding: 9px 22px;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  border-radius: var(--radius-pill);
  font-family: var(--font-body);
  font-size: 13px;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.btn-cancel:hover { background: var(--color-surface-hover); }

.btn-primary {
  padding: 9px 24px;
  background: var(--color-accent);
  color: white;
  border: none;
  border-radius: var(--radius-pill);
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background var(--transition-fast);
}

.btn-primary:hover:not(:disabled) { background: var(--color-accent-hover); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
