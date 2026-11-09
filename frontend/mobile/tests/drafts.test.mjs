import test from 'node:test'
import assert from 'node:assert/strict'
import { createDraftStore, createDraftBuffer, openDraft, initialTodoForm, itemVersionMatches } from '../src/utils/drafts.mjs'
import { flushEditors, protectEditor, safeReturnPath, tokenUserId, isCurrentUnauthorized, authFailureRedirect } from '../src/utils/editorProtection.mjs'

function storage() {
  const values = new Map()
  return {
    get length() { return values.size }, key: i => [...values.keys()][i],
    getItem: key => values.get(key) ?? null, setItem: (key, value) => values.set(key, value),
    removeItem: key => values.delete(key),
  }
}
function setup() {
  const disk = storage(), store = createDraftStore(disk, 'https://test/api:admin', 1)
  const form = initialTodoForm(null)
  const session = { store, copied: false, record: { id: 'draft-1', itemId: null, baseUpdatedAt: null, savedAt: null, form } }
  const buffer = createDraftBuffer(session, () => form)
  return { disk, store, form, session, buffer }
}
function locks() {
  const held = new Set()
  return { async request(name, _, callback) {
    if (held.has(name)) return callback(null)
    held.add(name)
    try { return await callback({ name }) } finally { held.delete(name) }
  } }
}

test('full long-form draft survives restart, with dates, tags, switch and status intact', () => {
  const { store, form, buffer } = setup()
  Object.assign(form, { title: '长篇草稿', description: '# 标题\n长文段落😀\n'.repeat(5000) + '![图片](/uploads/todo/test.png)',
    priority: 5, importance: 4, category_id: 7, tag_ids: [1, 3], due_date: '2026-11-10T13:35',
    scheduled_at: '2026-11-11T15:00', hasScheduled: true, status: 'paused' })
  buffer.flush()
  const restored = store.read('draft-1')
  assert.deepEqual(restored.form, form)
  assert.equal(store.list().items.length, 1)
})

test('empty opens do not litter draft list; clearing existing content is saved', () => {
  const { store, form, buffer } = setup()
  buffer.flush(); assert.equal(store.list().items.length, 0)
  form.title = 'temporary'; buffer.flush(); form.title = ''; buffer.flush()
  assert.equal(store.read('draft-1').form.title, '')
})

test('accounts, backends and apps are isolated, with independent keys', () => {
  const { disk, store, form, buffer } = setup()
  form.title = 'private'; buffer.flush()
  for (const [scope, user] of [['https://test/api:admin', 2], ['https://else/api:admin', 1], ['https://test/api:mobile', 1]]) {
    const other = createDraftStore(disk, scope, user)
    assert.equal(other.read('draft-1'), null)
    assert.equal(other.list().items.length, 0)
    other.save({ ...store.read('draft-1'), form: { ...form, title: 'other' } })
  }
  assert.equal(store.read('draft-1').form.title, 'private')
  assert.equal(disk.length, 4)
  assert.throws(() => createDraftStore(disk, 'scope', null))
  assert.throws(() => store.read('../other'))
})

test('quota/storage failure retains memory and last good backup, retry writes latest text', () => {
  const { disk, store, form, buffer } = setup()
  form.title = 'saved'; buffer.flush()
  const write = disk.setItem
  disk.setItem = () => { throw new Error('QuotaExceededError') }
  form.description = 'new text'
  assert.throws(() => buffer.flush())
  assert.equal(store.read('draft-1').form.description, '')
  assert.equal(form.description, 'new text')
  disk.setItem = write; buffer.flush()
  assert.equal(store.read('draft-1').form.description, 'new text')
})

test('failed/unknown server result keeps backup; successful submit only clears its draft', () => {
  const { store, session, form, buffer } = setup()
  form.title = 'pending publish'; buffer.flush(true)
  store.save({ ...session.record, id: 'another' })
  // No finish call on a rejected request or timeout.
  assert.equal(store.read('draft-1').form.title, 'pending publish')
  buffer.finish(); form.title = 'late callback'; buffer.flush()
  assert.equal(store.read('draft-1'), null)
  assert.equal(store.read('another').form.title, 'pending publish')
})

test('failed cleanup cannot re-enable submission, failed discard remains recoverable', () => {
  const { disk, store, form, buffer } = setup()
  form.title = 'submitted'; buffer.flush()
  disk.removeItem = () => { throw new Error('SecurityError') }
  assert.throws(() => buffer.discard())
  assert.equal(buffer.completed, false)
  assert.throws(() => buffer.finish())
  assert.equal(buffer.completed, true)
  assert.equal(store.read('draft-1').form.title, 'submitted')
})

test('corrupt/unsupported records stay on disk and are reported separately', () => {
  const { disk, store, form, buffer } = setup()
  form.title = 'good'; buffer.flush()
  disk.setItem(store.prefix + 'bad-json', '{')
  disk.setItem(store.prefix + 'bad-version', JSON.stringify({ version: 99 }))
  assert.equal(store.list().items.length, 1)
  disk.setItem(store.prefix + 'bad-date', JSON.stringify({ ...store.read('draft-1'), id: 'bad-date', savedAt: 42 }))
  assert.equal(store.list().unreadable.length, 3)
  assert.equal(disk.length, 4)
})

test('two tabs edit independent copies and never overwrite/remove the original', async () => {
  const { store, session, form, buffer } = setup()
  form.title = 'original'; buffer.flush()
  const api = locks()
  const first = await openDraft(store, session.record, { locks: api })
  const second = await openDraft(store, session.record, { locks: api, id: () => 'tab-two' })
  assert.equal(first.copied, false); assert.equal(second.copied, true)
  const secondForm = { ...second.record.form, title: 'tab two' }
  const secondBuffer = createDraftBuffer({ ...second, store }, () => secondForm)
  secondBuffer.flush()
  assert.equal(store.read('draft-1').form.title, 'original')
  assert.equal(store.read('tab-two').form.title, 'tab two')
  secondBuffer.finish()
  assert.ok(store.read('draft-1')); first.release(); second.release()
})

test('unsupported/denied Web Locks clones persisted drafts immediately; blank opens stay blank', async () => {
  const { store, session, form, buffer } = setup()
  const blank = await openDraft(store, session.record, { id: () => 'blank' })
  assert.equal(blank.copied, false)
  form.title = 'original'; buffer.flush()
  const denied = { request() { throw new Error('SecurityError') } }
  for (const api of [undefined, denied]) {
    const copy = await openDraft(store, session.record, { locks: api, id: () => api ? 'denied' : 'unsupported' })
    createDraftBuffer({ ...copy, store }, () => copy.record.form).flush()
    assert.equal(store.read(copy.record.id).form.title, 'original')
    copy.release()
  }
  assert.equal(store.list().items.length, 3)
})

test('a deleted draft cannot be resurrected from a stale list after acquiring its lock', async () => {
  const { store, session, form, buffer } = setup()
  form.title = 'done'; buffer.flush(); store.remove('draft-1')
  await assert.rejects(openDraft(store, session.record, { locks: locks() }), /提交或丢弃/)
})

test('version checks block stale/deleted edit targets and save-as-new persists new identity', () => {
  const { store, session, form, buffer } = setup()
  Object.assign(session.record, { itemId: 10, baseUpdatedAt: '2026-11-09T01:00:00Z' })
  const item = { id: 10, updated_at: session.record.baseUpdatedAt, is_deleted: false }
  assert.ok(itemVersionMatches(session.record, item))
  assert.ok(!itemVersionMatches(session.record, { ...item, updated_at: '2026-11-09T02:00:00Z' }))
  assert.ok(!itemVersionMatches(session.record, { ...item, is_deleted: true }))
  form.title = 'edit'; buffer.flush()
  Object.assign(session.record, { itemId: null, baseUpdatedAt: null }); buffer.flush()
  assert.equal(store.read('draft-1').itemId, null)
  assert.equal(store.read('draft-1').form.title, 'edit')
})

test('route/logout/401 guard flushes every editor and refuses navigation if any backup fails', () => {
  const { disk, store, form, buffer } = setup()
  let otherFlushed = false
  const off = protectEditor(() => { buffer.flush(); return true })
  const offOther = protectEditor(() => { otherFlushed = true; return true })
  try {
    form.title = 'last keystroke'; assert.equal(flushEditors(), true)
    assert.equal(store.read('draft-1').form.title, 'last keystroke')
    disk.setItem = () => { throw new Error('full') }; form.title = 'not yet saved'
    otherFlushed = false
    assert.equal(flushEditors(), false); assert.equal(otherFlushed, true)
  } finally { off(); offOther() }
  assert.equal(flushEditors(), true)
})

test('safe return keeps local query/hash but rejects external URLs and login loops', () => {
  assert.equal(safeReturnPath('/todo?draft=one#detail', '/home'), '/todo?draft=one#detail')
  for (const value of ['https://evil.test', '//evil.test', '/\\evil.test', '/\nevil', '/login?redirect=/todo', null, ['/todo']]) {
    assert.equal(safeReturnPath(value, '/home'), '/home')
  }
})

test('old/concurrent 401 and wrong login credentials cannot clear a newer session', () => {
  assert.ok(isCurrentUnauthorized('old', 'old', '/admin/todo/items'))
  assert.ok(!isCurrentUnauthorized('old', 'new', '/admin/todo/items'))
  assert.ok(!isCurrentUnauthorized('old', null, '/admin/todo/items'))
  assert.ok(!isCurrentUnauthorized(null, null, '/admin/auth/login'))
  assert.ok(isCurrentUnauthorized(null, null, '/admin/todo/items'))
  assert.equal(tokenUserId(`header.${btoa(JSON.stringify({ sub: '42' }))}.sig`), 42)
  assert.equal(tokenUserId('malformed'), null)
})


test('initial auth failures preserve the destination and never invalidate a newer login', () => {
  const target = '/todo?draft=recover-me'
  assert.deepEqual(authFailureRedirect('expired', null, target, 401), { path: '/login', query: { redirect: target, expired: '1' } })
  assert.deepEqual(authFailureRedirect('valid', 'valid', target, undefined), { path: '/login', query: { redirect: target, retry: '1' } })
  assert.equal(authFailureRedirect('old', 'new', target, 401), false)
})
