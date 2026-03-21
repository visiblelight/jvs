<template>
  <div class="ak-manager">
    <div class="ak-header">
      <h3 class="card-title">Access Key 管理</h3>
      <button class="btn-create" @click="showCreateModal = true">
        <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14"><path d="M8 2a.75.75 0 01.75.75v4.5h4.5a.75.75 0 010 1.5h-4.5v4.5a.75.75 0 01-1.5 0v-4.5h-4.5a.75.75 0 010-1.5h4.5v-4.5A.75.75 0 018 2z"/></svg>
        创建
      </button>
    </div>

    <div v-if="keys.length === 0" class="ak-empty">暂无 Access Key</div>

    <div v-else class="ak-list">
      <div v-for="ak in keys" :key="ak.id" class="ak-row">
        <div class="ak-info">
          <div class="ak-name">{{ ak.name }}</div>
          <div class="ak-key-row">
            <code class="ak-key">{{ visibleKeys[ak.id] ? ak.key : maskKey(ak.key) }}</code>
            <button class="icon-btn" :title="visibleKeys[ak.id] ? '隐藏' : '显示'" @click="toggleVisible(ak.id)">
              <svg v-if="!visibleKeys[ak.id]" viewBox="0 0 16 16" fill="currentColor" width="14" height="14"><path d="M8 3.5C4.136 3.5 1.093 6.328.126 7.685a.5.5 0 000 .63C1.093 9.672 4.136 12.5 8 12.5s6.907-2.828 7.874-4.185a.5.5 0 000-.63C14.907 6.328 11.864 3.5 8 3.5zM8 11a3 3 0 110-6 3 3 0 010 6z"/></svg>
              <svg v-else viewBox="0 0 16 16" fill="currentColor" width="14" height="14"><path d="M.143 2.31a.75.75 0 011.047-.167l13.5 9.5a.75.75 0 01-.88 1.214l-2.248-1.582C10.49 11.748 9.28 12.2 8 12.2c-3.864 0-6.907-2.828-7.874-4.185a.5.5 0 010-.63A13.108 13.108 0 013.07 4.661L.31 2.718a.75.75 0 01-.167-1.047zM5.38 7.37a3 3 0 003.975 2.268L5.38 7.37zm6.283 2.148l-1.418-.998A3 3 0 006.24 4.55l-1.514-1.066C5.746 3.328 6.848 3.2 8 3.2c3.864 0 6.907 2.828 7.874 4.185a.5.5 0 010 .63 13.1 13.1 0 01-2.462 2.462z"/></svg>
            </button>
            <button class="icon-btn" title="复制" @click="copyKey(ak.key)">
              <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14"><path d="M0 6.75C0 5.784.784 5 1.75 5h1.5a.75.75 0 010 1.5h-1.5a.25.25 0 00-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 00.25-.25v-1.5a.75.75 0 011.5 0v1.5A1.75 1.75 0 019.25 16h-7.5A1.75 1.75 0 010 14.25v-7.5z"/><path d="M5 1.75C5 .784 5.784 0 6.75 0h7.5C15.216 0 16 .784 16 1.75v7.5A1.75 1.75 0 0114.25 11h-7.5A1.75 1.75 0 015 9.25v-7.5zm1.75-.25a.25.25 0 00-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 00.25-.25v-7.5a.25.25 0 00-.25-.25h-7.5z"/></svg>
            </button>
            <span v-if="copiedId === ak.id" class="copied-tip">已复制</span>
          </div>
          <div class="ak-scopes">
            <span v-for="s in ak.scopes" :key="s" class="scope-tag">{{ scopeLabel(s) }}</span>
            <span v-if="ak.scopes.length === 0" class="no-scope">无权限</span>
          </div>
        </div>
        <div class="ak-actions">
          <button class="link-btn" @click="openEditScopes(ak)">编辑权限</button>
          <label class="switch">
            <input type="checkbox" :checked="ak.is_active" @change="toggleActive(ak)" />
            <span class="slider"></span>
          </label>
          <button class="link-btn link-btn--danger" @click="handleDelete(ak)">删除</button>
        </div>
      </div>
    </div>

    <!-- 创建弹窗 -->
    <Teleport to="body">
      <div v-if="showCreateModal" class="overlay" @click.self="showCreateModal = false">
        <div class="modal" @click.stop>
          <div class="modal-head">
            <h3>创建 Access Key</h3>
            <button class="close-btn" @click="showCreateModal = false">
              <svg viewBox="0 0 16 16" fill="currentColor" width="16" height="16"><path d="M3.72 3.72a.75.75 0 011.06 0L8 6.94l3.22-3.22a.75.75 0 111.06 1.06L9.06 8l3.22 3.22a.75.75 0 11-1.06 1.06L8 9.06l-3.22 3.22a.75.75 0 01-1.06-1.06L6.94 8 3.72 4.78a.75.75 0 010-1.06z"/></svg>
            </button>
          </div>
          <div class="modal-body">
            <div class="form-row">
              <label>名称</label>
              <input v-model="createForm.name" placeholder="Key 用途说明" />
            </div>
            <div class="form-row">
              <label>权限</label>
              <div class="scope-checks">
                <label v-for="s in availableScopes" :key="s.scope" class="scope-check">
                  <input type="checkbox" :value="s.scope" v-model="createForm.scopes" />
                  <span>{{ s.label }}</span>
                </label>
                <div v-if="availableScopes.length === 0" class="no-scope">暂无可用权限</div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-cancel" @click="showCreateModal = false">取消</button>
            <button class="btn-primary" @click="handleCreate" :disabled="!createForm.name">创建</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 创建成功弹窗 -->
    <Teleport to="body">
      <div v-if="newlyCreatedKey" class="overlay" @click.self="newlyCreatedKey = null">
        <div class="modal" @click.stop>
          <div class="modal-head">
            <h3>Key 已创建</h3>
            <button class="close-btn" @click="newlyCreatedKey = null">
              <svg viewBox="0 0 16 16" fill="currentColor" width="16" height="16"><path d="M3.72 3.72a.75.75 0 011.06 0L8 6.94l3.22-3.22a.75.75 0 111.06 1.06L9.06 8l3.22 3.22a.75.75 0 11-1.06 1.06L8 9.06l-3.22 3.22a.75.75 0 01-1.06-1.06L6.94 8 3.72 4.78a.75.75 0 010-1.06z"/></svg>
            </button>
          </div>
          <div class="modal-body">
            <p class="key-warning">请立即复制保存此 Key，关闭后将不再完整显示。</p>
            <div class="key-display">
              <code>{{ newlyCreatedKey }}</code>
              <button class="btn-copy" @click="copyKey(newlyCreatedKey)">
                {{ copiedId === 'new' ? '已复制' : '复制' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 编辑权限弹窗 -->
    <Teleport to="body">
      <div v-if="editingScopesAk" class="overlay" @click.self="editingScopesAk = null">
        <div class="modal" @click.stop>
          <div class="modal-head">
            <h3>编辑权限 — {{ editingScopesAk.name }}</h3>
            <button class="close-btn" @click="editingScopesAk = null">
              <svg viewBox="0 0 16 16" fill="currentColor" width="16" height="16"><path d="M3.72 3.72a.75.75 0 011.06 0L8 6.94l3.22-3.22a.75.75 0 111.06 1.06L9.06 8l3.22 3.22a.75.75 0 11-1.06 1.06L8 9.06l-3.22 3.22a.75.75 0 01-1.06-1.06L6.94 8 3.72 4.78a.75.75 0 010-1.06z"/></svg>
            </button>
          </div>
          <div class="modal-body">
            <div class="scope-checks">
              <label v-for="s in availableScopes" :key="s.scope" class="scope-check">
                <input type="checkbox" :value="s.scope" v-model="editScopes" />
                <span>{{ s.label }}</span>
              </label>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-cancel" @click="editingScopesAk = null">取消</button>
            <button class="btn-primary" @click="saveScopes">保存</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import * as api from '@/api/access-key'

const keys = ref([])
const availableScopes = ref([])
const visibleKeys = ref({})
const copiedId = ref(null)
const showCreateModal = ref(false)
const newlyCreatedKey = ref(null)
const editingScopesAk = ref(null)
const editScopes = ref([])

const createForm = reactive({ name: '', scopes: [] })

async function fetchKeys() {
  const { data } = await api.getAccessKeys()
  keys.value = data
}

async function fetchScopes() {
  const { data } = await api.getScopes()
  availableScopes.value = data
}

onMounted(() => {
  fetchKeys()
  fetchScopes()
})

function maskKey(key) {
  return key.substring(0, 8) + '••••••••'
}

function toggleVisible(id) {
  visibleKeys.value[id] = !visibleKeys.value[id]
}

function scopeLabel(scope) {
  const found = availableScopes.value.find(s => s.scope === scope)
  return found ? found.label : scope
}

async function copyKey(key) {
  await navigator.clipboard.writeText(key)
  copiedId.value = key === newlyCreatedKey.value ? 'new' : keys.value.find(k => k.key === key)?.id
  setTimeout(() => { copiedId.value = null }, 2000)
}

async function handleCreate() {
  const { data } = await api.createAccessKey({ name: createForm.name, scopes: createForm.scopes })
  showCreateModal.value = false
  newlyCreatedKey.value = data.key
  createForm.name = ''
  createForm.scopes = []
  await fetchKeys()
}

async function toggleActive(ak) {
  await api.updateAccessKey(ak.id, { is_active: !ak.is_active })
  await fetchKeys()
}

async function handleDelete(ak) {
  if (!confirm(`确定删除 "${ak.name}"？`)) return
  await api.deleteAccessKey(ak.id)
  await fetchKeys()
}

function openEditScopes(ak) {
  editingScopesAk.value = ak
  editScopes.value = [...ak.scopes]
}

async function saveScopes() {
  await api.updateAccessKey(editingScopesAk.value.id, { scopes: editScopes.value })
  editingScopesAk.value = null
  await fetchKeys()
}
</script>

<style scoped>
.ak-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--color-border-light);
}

.ak-header .card-title {
  margin: 0;
  padding: 0;
  border: none;
}

.btn-create {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  background: var(--color-accent);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-create:hover {
  background: var(--color-accent-hover);
}

.ak-empty {
  text-align: center;
  padding: 32px;
  color: var(--color-text-tertiary);
  font-size: 13px;
}

.ak-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ak-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  transition: background var(--transition-fast);
}

.ak-row:hover {
  background: var(--color-surface-hover);
}

.ak-info {
  flex: 1;
  min-width: 0;
}

.ak-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text);
  margin-bottom: 4px;
}

.ak-key-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
}

.ak-key {
  font-size: 12px;
  color: var(--color-text-secondary);
  background: var(--color-surface-hover);
  padding: 2px 8px;
  border-radius: 4px;
  font-family: 'SF Mono', 'Fira Code', monospace;
}

.icon-btn {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: none;
  color: var(--color-text-tertiary);
  cursor: pointer;
  border-radius: 4px;
  transition: all var(--transition-fast);
}

.icon-btn:hover {
  background: var(--color-surface-active);
  color: var(--color-text);
}

.copied-tip {
  font-size: 11px;
  color: var(--color-success);
  animation: fadeIn 0.15s ease;
}

.ak-scopes {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.scope-tag {
  font-size: 11px;
  padding: 1px 7px;
  border-radius: 4px;
  background: var(--color-accent-subtle);
  color: var(--color-accent-text);
}

.no-scope {
  font-size: 11px;
  color: var(--color-text-tertiary);
}

.ak-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
  margin-left: 16px;
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
.link-btn--danger { color: var(--color-danger); }

/* Toggle switch */
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

.switch input:checked + .slider {
  background: var(--color-accent);
}

.switch input:checked + .slider::before {
  transform: translateX(16px);
}

/* Modals */
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(4px);
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
  border-radius: var(--radius-lg);
  width: 480px;
  max-height: 70vh;
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

.modal-body {
  padding: 20px 24px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 16px 24px;
  border-top: 1px solid var(--color-border-light);
}

.form-row {
  margin-bottom: 16px;
}

.form-row label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary);
  margin-bottom: 6px;
}

.form-row input[type="text"],
.form-row input:not([type]) {
  width: 100%;
  padding: 9px 12px;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-family: var(--font-body);
  font-size: 13px;
  color: var(--color-text);
  background: var(--color-surface);
  outline: none;
}

.form-row input:focus {
  border-color: var(--color-accent);
}

.scope-checks {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.scope-check {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--color-text);
  cursor: pointer;
}

.scope-check input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: var(--color-accent);
}

.btn-cancel {
  padding: 8px 18px;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  border-radius: var(--radius-sm);
  font-family: var(--font-body);
  font-size: 13px;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-cancel:hover { background: var(--color-surface-hover); }

.btn-primary {
  padding: 8px 20px;
  background: var(--color-accent);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-primary:hover:not(:disabled) { background: var(--color-accent-hover); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

/* Key display after creation */
.key-warning {
  font-size: 13px;
  color: var(--color-warning);
  margin-bottom: 12px;
}

.key-display {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background: var(--color-surface-hover);
  border-radius: var(--radius-md);
}

.key-display code {
  flex: 1;
  font-size: 12px;
  font-family: 'SF Mono', 'Fira Code', monospace;
  color: var(--color-text);
  word-break: break-all;
}

.btn-copy {
  padding: 6px 14px;
  background: var(--color-accent);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  font-family: var(--font-body);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  flex-shrink: 0;
  transition: background var(--transition-fast);
}

.btn-copy:hover { background: var(--color-accent-hover); }
</style>
