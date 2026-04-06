<template>
  <div class="tick-page">
    <PageHeader title="打卡" back-to="/home" />

    <div class="tick-content">
      <div v-if="store.loading && !store.tasks.length" class="loading-hint">
        <div class="spinner" />
      </div>

      <div v-else-if="!store.tasks.length" class="empty-state">
        <svg viewBox="0 0 48 48" fill="none" width="48" height="48">
          <rect x="8" y="6" width="32" height="36" rx="3" stroke="currentColor" stroke-width="1.5"/>
          <path d="M16 20l5 5 8-10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <p>暂无打卡任务</p>
        <p class="empty-sub">在管理后台创建打卡任务后即可在此打卡</p>
      </div>

      <div v-else class="task-list">
        <div
          v-for="t in store.tasks" :key="t.id"
          class="tick-card"
          :class="{ ticked: t.ticked_this_period }"
        >
          <div class="card-top" @click="toggleExpand(t.id)">
            <div class="card-info">
              <span class="card-title">{{ t.title }}</span>
              <div class="card-meta">
                <span class="freq-badge">{{ freqLabel(t.frequency) }}</span>
                <span v-if="t.current_streak > 0" class="streak-badge">🔥 {{ t.current_streak }}</span>
                <span v-if="t.enable_points" class="points-badge">{{ t.total_points }} 分</span>
              </div>
            </div>
            <button
              v-if="!t.ticked_this_period"
              class="tick-btn"
              @click.stop="handleTick(t)"
              :disabled="tickingId === t.id"
            >
              <svg viewBox="0 0 24 24" fill="none" width="24" height="24">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
              </svg>
            </button>
            <div v-else class="ticked-icon" @click.stop>
              <svg viewBox="0 0 24 24" fill="none" width="24" height="24">
                <circle cx="12" cy="12" r="10" fill="var(--color-accent)"/>
                <path d="M7 12l4 4 6-7" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>

          <!-- 展开详情 -->
          <div v-if="expandedId === t.id" class="card-expand">
            <div v-if="t.description" class="expand-desc">{{ t.description }}</div>
            <div class="expand-stats">
              <span>连续 {{ t.current_streak }} 次</span>
              <span>共 {{ t.total_ticks }} 次</span>
              <span v-if="t.enable_points">{{ t.total_points }} 积分</span>
            </div>

            <!-- 打卡表单（未打卡时） -->
            <div v-if="!t.ticked_this_period" class="expand-form">
              <div v-if="t.enable_quality" class="quality-row">
                <span class="quality-label">评价</span>
                <div class="stars">
                  <button v-for="s in 5" :key="s" type="button" class="star-btn" :class="{ filled: tickForm.quality >= s }" @click="tickForm.quality = s">★</button>
                </div>
              </div>
              <textarea v-model="tickForm.note" placeholder="备注（可选）" rows="2" class="note-input"></textarea>
              <button class="btn-tick" @click="handleTickWithForm(t)" :disabled="tickingId === t.id">
                {{ tickingId === t.id ? '打卡中…' : '打 卡' }}
              </button>
            </div>

            <!-- 撤销（已打卡时） -->
            <div v-else class="expand-undo">
              <span class="ticked-text">✓ 本期已打卡</span>
              <button class="btn-undo" @click="handleUndo(t)" :disabled="tickingId === t.id">撤销</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import { useTickStore } from '@/stores/tick'
import * as api from '@/api/tick'

const store = useTickStore()
const expandedId = ref(null)
const tickingId = ref(null)
const tickForm = reactive({ quality: 0, note: '' })

function freqLabel(f) {
  return { daily: '每天', weekly: '每周', monthly: '每月' }[f] || f
}

function toggleExpand(id) {
  if (expandedId.value === id) {
    expandedId.value = null
  } else {
    expandedId.value = id
    tickForm.quality = 0
    tickForm.note = ''
  }
}

async function handleTick(t) {
  tickingId.value = t.id
  try {
    await api.doTick(t.id, {})
    await store.fetchTasks()
  } catch (e) {
    alert(e?.response?.data?.detail || '打卡失败')
  } finally {
    tickingId.value = null
  }
}

async function handleTickWithForm(t) {
  tickingId.value = t.id
  try {
    const body = {}
    if (t.enable_quality && tickForm.quality > 0) body.quality = tickForm.quality
    if (tickForm.note.trim()) body.note = tickForm.note.trim()
    await api.doTick(t.id, body)
    tickForm.quality = 0
    tickForm.note = ''
    await store.fetchTasks()
  } catch (e) {
    alert(e?.response?.data?.detail || '打卡失败')
  } finally {
    tickingId.value = null
  }
}

async function handleUndo(t) {
  if (!confirm('确定撤销本次打卡？')) return
  tickingId.value = t.id
  try {
    await api.undoTick(t.id)
    await store.fetchTasks()
  } catch (e) {
    alert(e?.response?.data?.detail || '撤销失败')
  } finally {
    tickingId.value = null
  }
}

onMounted(() => store.fetchTasks())
</script>

<style scoped>
.tick-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--color-bg);
}

.tick-content {
  flex: 1;
  overflow-y: auto;
  padding: 12px 16px 32px;
}

.loading-hint {
  display: flex;
  justify-content: center;
  padding: 48px;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 2.5px solid var(--color-border);
  border-top-color: var(--color-accent);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.empty-state {
  text-align: center;
  padding: 48px 16px;
  color: var(--color-text-tertiary);
}

.empty-state svg { margin-bottom: 12px; }
.empty-state p { font-size: 14px; margin-bottom: 4px; }
.empty-sub { font-size: 12px; }

.task-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tick-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  transition: box-shadow var(--transition-fast);
}

.tick-card.ticked { opacity: 0.75; }

.card-top {
  display: flex;
  align-items: center;
  padding: 14px 16px;
  gap: 12px;
  cursor: pointer;
}

.card-info { flex: 1; min-width: 0; }

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 4px;
}

.ticked .card-title { text-decoration: line-through; color: var(--color-text-tertiary); }

.card-meta {
  display: flex;
  align-items: center;
  gap: 6px;
}

.freq-badge {
  font-size: 11px;
  padding: 1px 7px;
  border-radius: 4px;
  background: var(--color-surface-hover);
  color: var(--color-text-secondary);
}

.streak-badge {
  font-size: 11px;
  color: var(--color-text-tertiary);
}

.points-badge {
  font-size: 11px;
  padding: 1px 7px;
  border-radius: 4px;
  background: var(--color-accent-subtle);
  color: var(--color-accent-text);
}

.tick-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: none;
  color: var(--color-border);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: color var(--transition-fast);
}

.tick-btn:active { color: var(--color-accent); transform: scale(0.9); }
.tick-btn:disabled { opacity: 0.5; }

.ticked-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

/* ── 展开区域 ── */
.card-expand {
  padding: 0 16px 14px;
  border-top: 1px solid var(--color-border-light);
}

.expand-desc {
  font-size: 13px;
  color: var(--color-text-secondary);
  line-height: 1.5;
  margin-top: 10px;
  white-space: pre-wrap;
}

.expand-stats {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: var(--color-text-tertiary);
  margin-top: 10px;
  padding: 8px 0;
}

.expand-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 10px;
}

.quality-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.quality-label {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.stars { display: flex; gap: 2px; }

.star-btn {
  border: none;
  background: none;
  font-size: 22px;
  cursor: pointer;
  color: var(--color-border);
  padding: 0 2px;
}

.star-btn.filled { color: #F59E0B; }

.note-input {
  width: 100%;
  padding: 8px 12px;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-md);
  font-family: var(--font-body);
  font-size: 13px;
  color: var(--color-text);
  background: var(--color-surface);
  resize: none;
  outline: none;
}

.note-input:focus { border-color: var(--color-accent); }

.btn-tick {
  align-self: flex-start;
  padding: 9px 28px;
  background: var(--color-accent);
  color: white;
  border: none;
  border-radius: var(--radius-pill);
  font-family: var(--font-body);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

.btn-tick:disabled { opacity: 0.5; }

.expand-undo {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 10px;
}

.ticked-text {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-success);
}

.btn-undo {
  padding: 6px 16px;
  border: 1.5px solid var(--color-border);
  background: none;
  border-radius: var(--radius-pill);
  font-family: var(--font-body);
  font-size: 12px;
  color: var(--color-text-secondary);
  cursor: pointer;
}

.btn-undo:active { border-color: var(--color-danger); color: var(--color-danger); }
.btn-undo:disabled { opacity: 0.5; }
</style>
