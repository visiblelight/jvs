const ID = /^[a-zA-Z0-9-]{1,80}$/
export const newDraftId = () => crypto.randomUUID()

export function createDraftStore(storage, scope, userId) {
  if (!Number.isInteger(userId) || userId <= 0) throw new Error('请先登录后再编辑')
  const prefix = `jvs:todo-draft:v1:${encodeURIComponent(scope)}:${userId}:`
  const key = id => {
    if (!ID.test(id || '')) throw new Error('草稿编号无效')
    return prefix + id
  }
  function read(id) {
    const raw = storage.getItem(key(id))
    if (raw === null) return null
    const record = JSON.parse(raw)
    if (record?.version !== 1 || record.id !== id || record.userId !== userId ||
        typeof record.form?.title !== 'string' || typeof record.form?.description !== 'string' ||
        !Array.isArray(record.form.tag_ids) || !record.form.tag_ids.every(Number.isInteger) ||
        typeof record.form.hasScheduled !== 'boolean' || typeof record.form.due_date !== 'string' ||
        typeof record.form.scheduled_at !== 'string' || !['pending', 'paused', 'completed', 'archived'].includes(record.form.status) ||
        ![1, 2, 3, 4, 5].includes(record.form.priority) || ![1, 2, 3, 4, 5].includes(record.form.importance) ||
        !(record.itemId === null || Number.isInteger(record.itemId)) ||
        !(record.form.category_id === null || Number.isInteger(record.form.category_id)) ||
        typeof record.savedAt !== 'string' || !Number.isFinite(Date.parse(record.savedAt))) {
      throw new Error('草稿数据无法读取，原始备份仍保留')
    }
    return record
  }
  return {
    prefix, read,
    save(record) {
      const value = { ...record, version: 1, userId }
      storage.setItem(key(record.id), JSON.stringify(value))
      return value
    },
    remove(id) { storage.removeItem(key(id)) },
    list() {
      const items = [], unreadable = []
      for (let i = 0; i < storage.length; i++) {
        const name = storage.key(i)
        if (!name?.startsWith(prefix)) continue
        try { const value = read(name.slice(prefix.length)); if (value) items.push(value) }
        catch { unreadable.push(name) }
      }
      items.sort((a, b) => b.savedAt.localeCompare(a.savedAt))
      return { items, unreadable }
    },
  }
}

export async function acquireDraftLock(name, locks) {
  if (!locks) return null
  try {
    return await new Promise(resolve => {
      locks.request(name, { ifAvailable: true }, lock => {
        if (!lock) { resolve(null); return }
        return new Promise(release => resolve(release))
      }).catch(() => resolve(null))
    })
  } catch { return null }
}

export async function openDraft(store, record, { locks, id = newDraftId } = {}) {
  let release = await acquireDraftLock(store.prefix + record.id, locks)
  try {
    // Re-read after acquiring the lock; another tab may have saved or removed it.
    if (record.savedAt) {
      record = store.read(record.id)
      if (!record) throw new Error('这份草稿已被提交或丢弃，请刷新草稿列表。')
    }
    if (release) return { record, release, copied: false }
    const copy = { ...record, id: id() }
    release = await acquireDraftLock(store.prefix + copy.id, locks)
    return { record: copy, release: release || (() => {}), copied: !!record.savedAt }
  } catch (error) { release?.(); throw error }
}

// Keep persistence independent of component lifetime so failed writes remain retryable.
export function createDraftBuffer(session, snapshot) {
  const contents = () => JSON.stringify({
    itemId: session.record.itemId, baseUpdatedAt: session.record.baseUpdatedAt, form: snapshot(),
  })
  const initial = contents()
  let saved = session.record.savedAt && !session.copied ? initial : null
  let completed = false
  return {
    get completed() { return completed },
    flush(force = false) {
      if (completed) return
      const current = contents()
      if (!force && (current === saved || (saved === null && current === initial && !session.copied))) return
      const record = { ...session.record, ...JSON.parse(current), savedAt: new Date().toISOString() }
      session.store.save(record) // If this throws, never advance the saved snapshot.
      Object.assign(session.record, record)
      saved = current
    },
    finish() { completed = true; session.store.remove(session.record.id) },
    discard() { session.store.remove(session.record.id); completed = true },
  }
}

export function itemVersionMatches(record, item) {
  return !!record.baseUpdatedAt && record.itemId === item.id &&
    record.baseUpdatedAt === item.updated_at && !item.is_deleted
}

export function initialTodoForm(item) {
  return {
    title: item?.title || '', description: item?.description || '',
    priority: item?.priority || 3, importance: item?.importance || 3,
    category_id: item?.category_id ?? null, tag_ids: item?.tags?.map(t => t.id) || [],
    status: item?.status || 'pending', due_date: '', scheduled_at: '', hasScheduled: !!item?.scheduled_at,
  }
}
