// Instants and date-only values are separate: never append Z to a date key.
export function parseInstant(value) {
  if (value instanceof Date || typeof value === 'number') return new Date(value)
  if (!value || !/^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}/.test(value)) return new Date(NaN)
  let text = value.replace(' ', 'T')
  // Compatibility with the pre-024 API, whose naive timestamps were UTC.
  if (!/(Z|[+-]\d{2}:?\d{2})$/i.test(text)) text += 'Z'
  return new Date(text)
}

export function formatInstant(value, options = {}) {
  if (!value) return ''
  const date = parseInstant(value)
  if (Number.isNaN(date.getTime())) return ''
  return date.toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', ...options,
  })
}

const pad = n => String(n).padStart(2, '0')
export function localDateKey(date = new Date()) {
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`
}

export function parseDateKey(value) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return new Date(NaN)
  const [year, month, day] = value.split('-').map(Number)
  const date = new Date(year, month - 1, day)
  return localDateKey(date) === value ? date : new Date(NaN)
}

export function formatLocalDatetime(value) {
  if (!value) return ''
  const date = parseInstant(value)
  if (Number.isNaN(date.getTime())) return ''
  return `${localDateKey(date)}T${pad(date.getHours())}:${pad(date.getMinutes())}`
}

export function localInputToISO(value) {
  if (!value) return null
  if (!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?$/.test(value)) throw new Error('请输入有效的本地日期和时间')
  const date = new Date(value)
  // Reject nonexistent local wall times (e.g. during a daylight-saving jump).
  if (Number.isNaN(date.getTime()) || formatLocalDatetime(date) !== value.slice(0, 16)) throw new Error('该本地时间不存在')
  return date.toISOString()
}

export function timeAgo(value, now = Date.now()) {
  if (!value) return ''
  const diff = now - parseInstant(value).getTime()
  if (!Number.isFinite(diff)) return ''
  const min = Math.floor(Math.max(0, diff) / 60000)
  if (min < 1) return '刚刚'
  if (min < 60) return `${min} 分钟前`
  if (min < 1440) return `${Math.floor(min / 60)} 小时前`
  if (min < 43200) return `${Math.floor(min / 1440)} 天前`
  return formatInstant(value)
}

export function businessDateKey(value = new Date(), timeZone = 'Asia/Shanghai') {
  const parts = new Intl.DateTimeFormat('en-US', { timeZone, year: 'numeric', month: '2-digit', day: '2-digit' }).formatToParts(value)
  const get = type => parts.find(p => p.type === type).value
  return `${get('year')}-${get('month')}-${get('day')}`
}
