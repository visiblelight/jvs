import { businessDateKey, parseInstant } from './datetime.mjs'

const utcDay = key => new Date(`${key}T00:00:00Z`)
const keyOf = date => date.toISOString().slice(0, 10)

export function periodKey(frequency, day) {
  if (frequency === 'daily') return day
  if (frequency === 'monthly') return day.slice(0, 7)
  const date = utcDay(day)
  date.setUTCDate(date.getUTCDate() + 4 - (date.getUTCDay() || 7))
  const year = date.getUTCFullYear()
  const week = Math.ceil(((date - new Date(Date.UTC(year, 0, 1))) / 86400000 + 1) / 7)
  return `${year}-W${String(week).padStart(2, '0')}`
}

export function periodBounds(frequency, key) {
  if (frequency === 'daily') return [key, key]
  if (frequency === 'monthly') {
    const [year, month] = key.split('-').map(Number)
    return [`${key}-01`, keyOf(new Date(Date.UTC(year, month, 0)))]
  }
  const [year, week] = key.split('-W').map(Number)
  const monday = new Date(Date.UTC(year, 0, 4))
  monday.setUTCDate(monday.getUTCDate() - ((monday.getUTCDay() || 7) - 1) + (week - 1) * 7)
  return [keyOf(monday), keyOf(new Date(monday.getTime() + 6 * 86400000))]
}

export function calendarLogDate(log, timeZone = 'Asia/Shanghai') {
  if (!log.is_makeup) return businessDateKey(parseInstant(log.ticked_at), timeZone)
  const frequency = /^\d{4}-\d{2}-\d{2}$/.test(log.period_key) ? 'daily' : log.period_key.includes('-W') ? 'weekly' : 'monthly'
  return periodBounds(frequency, log.period_key)[1]
}

export function nextBusinessDayDelay(now, timeZone) {
  const day = businessDateKey(new Date(now), timeZone)
  let low = now, high = now + 48 * 3600000
  while (high - low > 1) {
    const mid = Math.floor((low + high) / 2)
    if (businessDateKey(new Date(mid), timeZone) === day) low = mid
    else high = mid
  }
  return high - now + 100 // cross the boundary even with small timer rounding
}

export function watchBusinessDay(refresh, timezone, env = {}) {
  const now = env.now || Date.now
  const schedule = env.setTimeout || globalThis.setTimeout
  const cancel = env.clearTimeout || globalThis.clearTimeout
  const doc = env.document || globalThis.document
  const onError = env.onError || (error => console.warn('跨天刷新失败，将重试', error))
  let last = businessDateKey(new Date(now()), timezone())
  let timer, stopped = false, running = false
  const arm = delay => { if (!stopped) { cancel(timer); timer = schedule(check, delay) } }
  const check = async () => {
    if (stopped || running) return
    running = true
    let retry = false
    try {
      const day = businessDateKey(new Date(now()), timezone())
      if (day !== last) { await refresh(); last = day }
    } catch (error) { retry = true; onError(error) }
    finally {
      running = false
      arm(retry ? 60000 : nextBusinessDayDelay(now(), timezone()))
    }
  }
  const visible = () => { if (doc.visibilityState === 'visible') check() }
  doc.addEventListener('visibilitychange', visible)
  arm(nextBusinessDayDelay(now(), timezone()))
  return () => { stopped = true; cancel(timer); doc.removeEventListener('visibilitychange', visible) }
}
