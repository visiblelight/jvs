<template>
  <div class="cal-root">

    <!-- ══ Toolbar ══ -->
    <div class="cal-toolbar">
      <div class="toolbar-left">
        <button class="arrow-btn" @click="navigate(-1)" aria-label="上一期">
          <svg viewBox="0 0 16 16" fill="currentColor" width="15" height="15">
            <path fill-rule="evenodd" d="M9.78 4.22a.75.75 0 010 1.06L7.06 8l2.72 2.72a.75.75 0 11-1.06 1.06L5.47 8.53a.75.75 0 010-1.06l3.25-3.25a.75.75 0 011.06 0z"/>
          </svg>
        </button>
        <h2 class="cal-period">{{ periodLabel }}</h2>
        <button class="arrow-btn" @click="navigate(1)" aria-label="下一期">
          <svg viewBox="0 0 16 16" fill="currentColor" width="15" height="15">
            <path fill-rule="evenodd" d="M6.22 4.22a.75.75 0 011.06 0l3.25 3.25a.75.75 0 010 1.06l-3.25 3.25a.75.75 0 01-1.06-1.06L8.94 8 6.22 5.28a.75.75 0 010-1.06z"/>
          </svg>
        </button>
      </div>

      <div class="toolbar-right">
        <button class="today-pill" :class="{ active: isCurrentPeriod }" @click="goToday">今日</button>
        <div class="mode-tabs">
          <button
            v-for="m in viewModes" :key="m.value"
            class="mode-tab"
            :class="{ active: mode === m.value }"
            @click="mode = m.value"
          >{{ m.label }}</button>
        </div>
      </div>
    </div>

    <!-- ══ Day View ══ -->
    <div v-if="mode === 'day'" class="day-root">
      <div class="day-date-banner">
        <span class="day-weekname">{{ WEEK_CN[cursor.getDay()] }}</span>
        <span class="day-num" :class="{ today: isToday(cursor) }">{{ cursor.getDate() }}</span>
      </div>
      <div class="agenda-scroll">
        <div v-if="dayItems.length === 0" class="empty-state">
          <svg viewBox="0 0 48 48" fill="none" width="40" height="40">
            <rect x="6" y="10" width="36" height="30" rx="5" stroke="currentColor" stroke-width="1.5"/>
            <path d="M16 6v8M32 6v8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            <path d="M14 26h20M14 33h12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
          <p>今日无安排</p>
        </div>
        <div
          v-for="item in dayItems" :key="item.id + item._type"
          class="agenda-card" :class="'agenda-card--' + item._type"
          @click="store.selectItem(item.id)"
        >
          <div class="agenda-stripe"></div>
          <div class="agenda-time-col">
            <span class="agenda-type-icon">{{ item._type === 'scheduled' ? '🕐' : '📅' }}</span>
            <span class="agenda-time-text">
              {{ item._type === 'scheduled' ? formatTime(item.scheduled_at) : '截止' }}
            </span>
          </div>
          <div class="agenda-body">
            <p class="agenda-title" :class="{ done: item.status === 'completed' }">{{ item.title }}</p>
            <div class="agenda-meta">
              <span class="meta-type">{{ item._type === 'scheduled' ? '执行时间' : '截止时间' }}</span>
              <span v-for="tag in item.tags" :key="tag.id" class="meta-tag" :style="{ '--tc': tag.color }">{{ tag.name }}</span>
            </div>
          </div>
          <span class="agenda-status-dot" :class="'dot-' + item.status"></span>
        </div>
      </div>
    </div>

    <!-- ══ Week View ══ -->
    <div v-if="mode === 'week'" class="week-root">
      <div class="week-header">
        <div v-for="(day, i) in weekDays" :key="i" class="week-head-cell">
          <span class="wh-name">{{ DAY_NAMES[i] }}</span>
          <span class="wh-num" :class="{ today: isToday(day.date) }">{{ day.date.getDate() }}</span>
        </div>
      </div>
      <div class="week-body">
        <div v-for="(day, i) in weekDays" :key="i" class="week-col" :class="{ 'week-col--today': isToday(day.date) }">
          <div
            v-for="item in day.items" :key="item.id + item._type"
            class="week-chip" :class="'week-chip--' + item._type"
            @click="store.selectItem(item.id)"
          >
            <span class="chip-icon">{{ item._type === 'scheduled' ? '🕐' : '📅' }}</span>
            <span v-if="item._type === 'scheduled'" class="chip-time">{{ formatTime(item.scheduled_at) }}</span>
            <span class="chip-title">{{ item.title }}</span>
          </div>
          <div v-if="day.items.length === 0" class="week-col-empty"></div>
        </div>
      </div>
    </div>

    <!-- ══ Month View ══ -->
    <div v-if="mode === 'month'" class="month-root">
      <div class="month-dow-row">
        <span v-for="d in DAY_NAMES" :key="d" class="dow-label">{{ d }}</span>
      </div>
      <div class="month-grid">
        <div
          v-for="(cell, i) in monthCells" :key="i"
          class="month-cell"
          :class="{
            'month-cell--out': !cell.inMonth,
            'month-cell--today': isToday(cell.date),
            'month-cell--weekend': cell.date.getDay() === 0 || cell.date.getDay() === 6,
          }"
        >
          <div class="cell-head">
            <span class="cell-num" :class="{ today: isToday(cell.date) }">{{ cell.date.getDate() }}</span>
          </div>
          <div class="cell-events">
            <button
              v-for="item in cell.items.slice(0, 3)" :key="item.id + item._type"
              class="cell-event" :class="'cell-event--' + item._type"
              @click.stop="store.selectItem(item.id)"
            >
              <span class="event-icon">{{ item._type === 'scheduled' ? '🕐' : '📅' }}</span>
              <span class="event-text">{{ item.title }}</span>
            </button>
            <span v-if="cell.items.length > 3" class="cell-more">+{{ cell.items.length - 3 }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ══ Year View ══ -->
    <div v-if="mode === 'year'" class="year-root">
      <div class="year-grid">
        <div
          v-for="m in yearMonths" :key="m.month"
          class="year-card"
          :class="{ 'year-card--current': m.month === new Date().getMonth() && cursor.getFullYear() === new Date().getFullYear() }"
          @click="jumpToMonth(m.month)"
        >
          <div class="ycard-header">
            <span class="ycard-name">{{ MONTH_NAMES[m.month] }}</span>
            <span v-if="m.count > 0" class="ycard-count">{{ m.count }}</span>
          </div>
          <div class="ycard-mini">
            <span v-for="d in DOW_LABELS_SHORT" :key="d" class="mini-dow">{{ d }}</span>
            <div
              v-for="(cell, i) in m.cells" :key="i"
              class="mini-cell"
              :class="{
                'mini-cell--out': !cell.inMonth,
                'mini-cell--today': isToday(cell.date),
                'mini-cell--has': cell.count > 0 && cell.inMonth,
              }"
            >{{ cell.inMonth ? cell.date.getDate() : '' }}</div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useTodoStore } from '@/stores/todo'

const store = useTodoStore()

// ── Constants ──────────────────────────────────────────────────────────────
const DAY_NAMES       = ['日', '一', '二', '三', '四', '五', '六']
const WEEK_CN         = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
const DOW_LABELS_SHORT = ['日', '一', '二', '三', '四', '五', '六']
const MONTH_NAMES     = ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月']
const viewModes       = [
  { value: 'day',   label: '日' },
  { value: 'week',  label: '周' },
  { value: 'month', label: '月' },
  { value: 'year',  label: '年' },
]

// ── State ─────────────────────────────────────────────────────────────────
const mode   = ref('month')
// Store as timestamp to guarantee Vue detects all changes
const cursorTs = ref(startOfDay(new Date()).getTime())
const cursor   = computed(() => new Date(cursorTs.value))

// ── Helpers ───────────────────────────────────────────────────────────────
function startOfDay(d) {
  return new Date(d.getFullYear(), d.getMonth(), d.getDate())
}

function isToday(d) {
  const t = new Date()
  return d.getFullYear() === t.getFullYear() && d.getMonth() === t.getMonth() && d.getDate() === t.getDate()
}

function sameDay(a, b) {
  return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate()
}

function formatTime(dt) {
  if (!dt) return ''
  const d = new Date(dt)
  return `${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
}

function weekStart(d) {
  const ws = new Date(d)
  ws.setDate(ws.getDate() - ws.getDay())
  ws.setHours(0, 0, 0, 0)
  return ws
}

// ── "今日" active indicator ────────────────────────────────────────────────
// "今日" 按钮仅在日视图看今天时高亮，其余情况保持可点击外观
const isCurrentPeriod = computed(() => mode.value === 'day' && isToday(cursor.value))

// ── Period label ──────────────────────────────────────────────────────────
const periodLabel = computed(() => {
  const d = cursor.value
  if (mode.value === 'day') {
    return `${d.getFullYear()}年${d.getMonth()+1}月${d.getDate()}日`
  }
  if (mode.value === 'week') {
    const ws = weekStart(d)
    const we = new Date(ws); we.setDate(we.getDate() + 6)
    if (ws.getMonth() === we.getMonth())
      return `${ws.getFullYear()}年${ws.getMonth()+1}月`
    return `${ws.getMonth()+1}月${ws.getDate()}日 — ${we.getMonth()+1}月${we.getDate()}日`
  }
  if (mode.value === 'month') return `${d.getFullYear()}年${d.getMonth()+1}月`
  return `${d.getFullYear()}年`
})

// ── Navigation ────────────────────────────────────────────────────────────
function navigate(dir) {
  const d = new Date(cursor.value)
  if      (mode.value === 'day')   d.setDate(d.getDate() + dir)
  else if (mode.value === 'week')  d.setDate(d.getDate() + dir * 7)
  else if (mode.value === 'month') d.setMonth(d.getMonth() + dir)
  else                              d.setFullYear(d.getFullYear() + dir)
  cursorTs.value = startOfDay(d).getTime()
}

function goToday() {
  cursorTs.value = startOfDay(new Date()).getTime()
  mode.value = 'day'
  loadData()
}

function jumpToMonth(month) {
  const d = new Date(cursor.value.getFullYear(), month, 1)
  cursorTs.value = d.getTime()
  mode.value = 'month'
}

// ── Expand items (one item may appear as both scheduled + due) ─────────────
function expandItems(items) {
  const result = []
  for (const item of items) {
    if (item.scheduled_at) result.push({ ...item, _type: 'scheduled', _date: new Date(item.scheduled_at) })
    else if (item.due_date) result.push({ ...item, _type: 'due',      _date: new Date(item.due_date) })
  }
  return result.sort((a, b) => a._date - b._date)
}

// ── Range for API fetch ───────────────────────────────────────────────────
function getRange() {
  const d = cursor.value
  if (mode.value === 'day') {
    const start = startOfDay(d)
    const end   = new Date(start); end.setDate(end.getDate() + 1)
    return { start, end }
  }
  if (mode.value === 'week') {
    const start = weekStart(d)
    const end   = new Date(start); end.setDate(end.getDate() + 7)
    return { start, end }
  }
  if (mode.value === 'month') {
    const first = new Date(d.getFullYear(), d.getMonth(), 1)
    const gs    = new Date(first); gs.setDate(gs.getDate() - gs.getDay())
    const last  = new Date(d.getFullYear(), d.getMonth() + 1, 0)
    const ge    = new Date(last); ge.setDate(ge.getDate() + (6 - ge.getDay()) + 1)
    return { start: gs, end: ge }
  }
  return { start: new Date(d.getFullYear(), 0, 1), end: new Date(d.getFullYear() + 1, 0, 1) }
}

// ── Computed views ────────────────────────────────────────────────────────
const dayItems = computed(() => {
  return expandItems(store.calendarItems).filter(e => sameDay(e._date, cursor.value))
})

const weekDays = computed(() => {
  const ws = weekStart(cursor.value)
  const expanded = expandItems(store.calendarItems)
  return Array.from({ length: 7 }, (_, i) => {
    const date = new Date(ws); date.setDate(date.getDate() + i)
    return { date, items: expanded.filter(e => sameDay(e._date, date)) }
  })
})

const monthCells = computed(() => {
  const d = cursor.value
  const first = new Date(d.getFullYear(), d.getMonth(), 1)
  const gs = new Date(first); gs.setDate(gs.getDate() - gs.getDay())
  const expanded = expandItems(store.calendarItems)
  const cur = new Date(gs)
  return Array.from({ length: 42 }, () => {
    const date = new Date(cur); cur.setDate(cur.getDate() + 1)
    return { date, inMonth: date.getMonth() === d.getMonth(), items: expanded.filter(e => sameDay(e._date, date)) }
  })
})

const yearMonths = computed(() => {
  const y = cursor.value.getFullYear()
  const expanded = expandItems(store.calendarItems)
  return Array.from({ length: 12 }, (_, m) => {
    const first = new Date(y, m, 1)
    const gs = new Date(first); gs.setDate(gs.getDate() - gs.getDay())
    const cur = new Date(gs)
    let count = 0
    const cells = Array.from({ length: 42 }, () => {
      const date = new Date(cur); cur.setDate(cur.getDate() + 1)
      const inMonth = date.getMonth() === m && date.getFullYear() === y
      const dayCount = inMonth ? expanded.filter(e => sameDay(e._date, date)).length : 0
      if (dayCount) count += dayCount
      return { date, inMonth, count: dayCount }
    })
    return { month: m, cells, count }
  })
})

// ── Data loading ──────────────────────────────────────────────────────────
function loadData() {
  const { start, end } = getRange()
  store.fetchCalendarItems(start, end)
}

watch([mode, cursorTs], loadData)
onMounted(loadData)
</script>

<style scoped>
/* ── Root ── */
.cal-root {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
  background: var(--color-surface);
}

/* ══════════════════════════════════════════
   Toolbar
══════════════════════════════════════════ */
.cal-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  border-bottom: 1px solid var(--color-border-light);
  flex-shrink: 0;
  gap: 12px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 6px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* Arrow buttons */
.arrow-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  background: none;
  border-radius: 8px;
  color: var(--color-text-tertiary);
  cursor: pointer;
  transition: all var(--transition-fast);
}
.arrow-btn:hover {
  background: var(--color-surface-hover);
  color: var(--color-text);
}
.arrow-btn:active { transform: scale(0.9); }

/* Period label */
.cal-period {
  font-family: var(--font-heading);
  font-size: 17px;
  font-weight: 700;
  color: var(--color-text);
  margin: 0;
  min-width: 140px;
  text-align: center;
  letter-spacing: -0.02em;
}

/* Today pill */
.today-pill {
  padding: 5px 14px;
  border: 1.5px solid var(--color-border);
  background: none;
  border-radius: var(--radius-pill);
  font-family: var(--font-body);
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
}
.today-pill:hover,
.today-pill.active {
  border-color: var(--color-accent);
  color: var(--color-accent-text);
  background: var(--color-accent-subtle);
}

/* Mode tabs — pill row, no container background */
.mode-tabs {
  display: flex;
  align-items: center;
  gap: 2px;
  background: var(--color-bg-base);
  border-radius: var(--radius-pill);
  padding: 3px;
}

.mode-tab {
  padding: 5px 14px;
  border: none;
  background: transparent;
  border-radius: var(--radius-pill);
  font-family: var(--font-body);
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-tertiary);
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
}
.mode-tab:hover { color: var(--color-text); }
.mode-tab.active {
  background: var(--color-surface-raised, white);
  color: var(--color-accent-text);
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}

/* ══════════════════════════════════════════
   Day View
══════════════════════════════════════════ */
.day-root {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.day-date-banner {
  display: flex;
  align-items: baseline;
  gap: 8px;
  padding: 16px 24px 12px;
  border-bottom: 1px solid var(--color-border-light);
  flex-shrink: 0;
}

.day-weekname {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.day-num {
  font-family: var(--font-heading);
  font-size: 32px;
  font-weight: 800;
  color: var(--color-text);
  line-height: 1;
}
.day-num.today {
  color: var(--color-accent);
}

.agenda-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 16px 24px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: 60px;
  color: var(--color-text-tertiary);
  font-size: 13px;
}

.agenda-card {
  display: flex;
  align-items: center;
  gap: 0;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border-light);
  overflow: hidden;
  cursor: pointer;
  transition: all var(--transition-fast);
  background: var(--color-surface-raised);
}
.agenda-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.agenda-stripe {
  width: 4px;
  align-self: stretch;
  flex-shrink: 0;
}
.agenda-card--scheduled .agenda-stripe { background: var(--color-accent); }
.agenda-card--due       .agenda-stripe { background: var(--color-warning); }

.agenda-time-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  width: 56px;
  flex-shrink: 0;
  padding: 14px 0;
}
.agenda-type-icon {
  font-size: 18px;
  line-height: 1;
}

.agenda-time-text {
  font-size: 11px;
  font-weight: 700;
  color: var(--color-text-secondary);
  letter-spacing: 0.3px;
}

.agenda-body {
  flex: 1;
  padding: 12px 14px;
  min-width: 0;
}

.agenda-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
  margin: 0 0 5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.agenda-title.done {
  text-decoration: line-through;
  color: var(--color-text-tertiary);
}

.agenda-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.meta-type {
  font-size: 10px;
  font-weight: 600;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.meta-tag {
  font-size: 10px;
  font-weight: 600;
  padding: 1px 6px;
  border-radius: 4px;
  background: color-mix(in srgb, var(--tc) 12%, transparent);
  color: var(--tc);
}

.agenda-status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 14px;
  flex-shrink: 0;
}
.dot-pending   { background: var(--color-status-pending); }
.dot-paused    { background: var(--color-status-paused); }
.dot-completed { background: var(--color-status-completed); }

/* ══════════════════════════════════════════
   Week View
══════════════════════════════════════════ */
.week-root {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.week-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  border-bottom: 1px solid var(--color-border-light);
  flex-shrink: 0;
}

.week-head-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 10px 4px;
  border-right: 1px solid var(--color-border-light);
}
.week-head-cell:last-child { border-right: none; }

.wh-name {
  font-size: 11px;
  font-weight: 700;
  color: var(--color-text-tertiary);
  letter-spacing: 0.4px;
}

.wh-num {
  font-family: var(--font-heading);
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}
.wh-num.today {
  background: var(--color-accent);
  color: white;
}

.week-body {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  overflow-y: auto;
}

.week-col {
  border-right: 1px solid var(--color-border-light);
  padding: 8px 4px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.week-col:last-child { border-right: none; }
.week-col--today { background: rgba(99, 102, 241, 0.03); }

.week-chip {
  display: flex;
  flex-direction: column;
  gap: 1px;
  padding: 5px 7px;
  border-radius: 7px;
  cursor: pointer;
  font-size: 11px;
  transition: all var(--transition-fast);
  border-left: 2px solid transparent;
}
.week-chip--scheduled {
  background: var(--color-accent-subtle);
  border-left-color: var(--color-accent);
}
.week-chip--due {
  background: rgba(234, 179, 8, 0.08);
  border-left-color: var(--color-warning);
}
.week-chip:hover { box-shadow: var(--shadow-sm); transform: translateY(-1px); }

.chip-icon {
  font-size: 11px;
  flex-shrink: 0;
  line-height: 1;
}

.chip-time {
  font-size: 10px;
  font-weight: 700;
  color: var(--color-text-secondary);
  letter-spacing: 0.3px;
}

.chip-title {
  font-weight: 600;
  color: var(--color-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.3;
}

.week-col-empty { flex: 1; }

/* ══════════════════════════════════════════
   Month View
══════════════════════════════════════════ */
.month-root {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.month-dow-row {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  border-bottom: 1px solid var(--color-border-light);
  flex-shrink: 0;
}

.dow-label {
  text-align: center;
  padding: 8px 0;
  font-size: 11px;
  font-weight: 700;
  color: var(--color-text-tertiary);
  letter-spacing: 0.5px;
}

.month-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  grid-auto-rows: 1fr;
  overflow: hidden;
}

.month-cell {
  border-right: 1px solid var(--color-border-light);
  border-bottom: 1px solid var(--color-border-light);
  padding: 6px 6px 4px;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
  transition: background var(--transition-fast);
}
.month-cell:nth-child(7n) { border-right: none; }

.month-cell--out { opacity: 0.3; }

.month-cell--weekend:not(.month-cell--out) {
  background: rgba(0, 0, 0, 0.012);
}
[data-theme="dark"] .month-cell--weekend:not(.month-cell--out) {
  background: rgba(255,255,255,0.012);
}

.month-cell--today {
  background: var(--color-accent-subtle) !important;
}

.cell-head {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 3px;
}

.cell-num {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-secondary);
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  flex-shrink: 0;
}
.cell-num.today {
  background: var(--color-accent);
  color: white;
  font-weight: 700;
}

.cell-events {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow: hidden;
  min-height: 0;
}

.cell-event {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 2px 5px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  text-align: left;
  transition: all var(--transition-fast);
  overflow: hidden;
  white-space: nowrap;
  width: 100%;
  line-height: 1.5;
}
.cell-event--scheduled {
  background: var(--color-accent-subtle);
  color: var(--color-accent-text);
}
.cell-event--due {
  background: rgba(234, 179, 8, 0.1);
  color: color-mix(in srgb, var(--color-warning) 80%, var(--color-text));
}
.cell-event:hover { filter: brightness(0.95); }

.event-icon {
  font-size: 10px;
  flex-shrink: 0;
  line-height: 1;
}

.event-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.cell-more {
  font-size: 10px;
  font-weight: 600;
  color: var(--color-text-tertiary);
  padding: 0 5px;
  cursor: default;
}

/* ══════════════════════════════════════════
   Year View
══════════════════════════════════════════ */
.year-root {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
}

.year-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.year-card {
  background: var(--color-surface-raised);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  padding: 14px;
  cursor: pointer;
  transition: all var(--transition-fast);
}
.year-card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--color-accent);
  transform: translateY(-2px);
}
.year-card--current {
  border-color: var(--color-accent);
  background: var(--color-accent-subtle);
}

.ycard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.ycard-name {
  font-size: 13px;
  font-weight: 700;
  color: var(--color-text);
}

.ycard-count {
  font-size: 11px;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 8px;
  background: var(--color-accent-subtle);
  color: var(--color-accent-text);
}

.ycard-mini {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
}

.mini-dow {
  font-size: 8px;
  font-weight: 600;
  color: var(--color-text-tertiary);
  text-align: center;
  padding: 2px 0;
}

.mini-cell {
  font-size: 8px;
  text-align: center;
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 2px;
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
}
.mini-cell--out { visibility: hidden; }
.mini-cell--today {
  background: var(--color-accent);
  color: white;
  font-weight: 700;
  border-radius: 50%;
}
.mini-cell--has {
  background: var(--color-accent-subtle);
  color: var(--color-accent-text);
  font-weight: 700;
  border-radius: 3px;
}
</style>
