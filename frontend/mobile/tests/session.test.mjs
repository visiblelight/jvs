import test from 'node:test'
import assert from 'node:assert/strict'
import axios, { AxiosError } from 'axios'
import { createSessionManager, needsRenewal, sameSession } from '../src/utils/session.mjs'
import { installSessionInterceptors } from '../src/utils/sessionRequests.mjs'

const now = 1_800_000_000_000
const token = (extra = {}) => `header.${btoa(JSON.stringify({ sub: '1', sid: 'session-one', ver: 0, iat: now / 1000 - 3600, exp: now / 1000 + 3600, ...extra }))}.signature`
const old = token({ exp: now / 1000 - 1 }), fresh = token({ exp: now / 1000 + 7200 })
function memory(initial = {}) {
  const values = new Map(Object.entries(initial))
  return { getItem: k => values.get(k) ?? null, setItem: (k, v) => values.set(k, v), removeItem: k => values.delete(k) }
}
function setup(initial = old, customTransport, storage = memory(), locks) {
  if (initial) storage.setItem('token', initial)
  const calls = []
  const session = createSessionManager({ storage, locks, now: () => now, randomId: () => Math.random().toString(),
    transport: async (action, body) => {
      calls.push({ action, body })
      return customTransport ? customTransport(action, body) : { data: { access_token: fresh } }
    } })
  return { session, storage, calls }
}
const failure = status => Object.assign(new Error(`HTTP ${status}`), { response: { status } })
const defer = () => { let resolve, reject; const promise = new Promise((a, b) => { resolve = a; reject = b }); return { promise, resolve, reject } }
const success = config => ({ status: 200, data: 'ok', headers: {}, config })
function rejectRequest(config, status = 401) {
  throw new AxiosError('Failed', 'ERR_BAD_REQUEST', config, null, { status, data: {}, headers: {}, config })
}
function http(session, adapter) {
  const client = axios.create({ adapter })
  let expirations = 0
  installSessionInterceptors(client, { session, expire: async error => {
    if (session.invalidate(error.config._authToken)) expirations++
  } })
  return { client, expirations: () => expirations }
}

test('renew near expiry, with adaptive lead for short-lived tests and no early legacy logout', () => {
  assert.equal(needsRenewal(old, now), true)
  assert.equal(needsRenewal(fresh, now), false)
  assert.equal(needsRenewal(token({ iat: now / 1000 - 59, exp: now / 1000 + 1 }), now), true)
  assert.equal(needsRenewal(token({ sid: undefined, exp: now / 1000 + 1 }), now), false)
  assert.equal(sameSession(old, fresh), true)
  assert.equal(sameSession(fresh, token({ sid: 'another' })), false)
})

test('many expired-token requests share one proactive refresh before any business write', async () => {
  const { session, calls } = setup()
  let writes = 0
  const { client } = http(session, async config => {
    assert.equal(config.headers.Authorization, `Bearer ${fresh}`)
    writes++; return success(config)
  })
  await Promise.all(Array.from({ length: 20 }, () => client.post('/todo', { title: 'draft' })))
  assert.equal(calls.length, 1); assert.equal(writes, 20)
})

test('business 401 refreshes then retries only once, preserving method and payload', async () => {
  const original = token()
  const { session, calls } = setup(original)
  let requests = 0
  const { client } = http(session, async config => {
    requests++
    assert.equal(config.method, 'post'); assert.equal(JSON.parse(config.data).title, 'long draft')
    if (config.headers.Authorization === `Bearer ${original}`) rejectRequest(config)
    return success(config)
  })
  await client.post('/todo', { title: 'long draft' })
  assert.equal(calls.length, 1); assert.equal(requests, 2)
})

test('repeated 401 stops after one retry and expires the matching session', async () => {
  const { session, calls, storage } = setup(token())
  let attempts = 0
  const { client, expirations } = http(session, async config => { attempts++; rejectRequest(config) })
  await assert.rejects(client.get('/me'))
  assert.equal(attempts, 2); assert.equal(calls.length, 1)
  assert.equal(expirations(), 1); assert.equal(storage.getItem('token'), null)
})

for (const error of [failure(503), Object.assign(new Error('offline'), { code: 'ERR_NETWORK' }), Object.assign(new Error('timeout'), { code: 'ECONNABORTED' })]) {
  test(`temporary renewal failure keeps authentication and does not replay writes: ${error.message}`, async () => {
    const { session, storage } = setup(old, async () => { throw error })
    let writes = 0
    const { client, expirations } = http(session, async config => { writes++; return success(config) })
    await assert.rejects(client.post('/todo', { text: 'keep' }))
    assert.equal(storage.getItem('token'), old); assert.equal(expirations(), 0); assert.equal(writes, 0)
  })
}

test('business 500 is not replayed and does not trigger renewal', async () => {
  const { session, calls } = setup(token())
  let attempts = 0
  const { client, expirations } = http(session, async config => { attempts++; rejectRequest(config, 500) })
  await assert.rejects(client.post('/todo', {}))
  assert.equal(attempts, 1); assert.equal(calls.length, 0); assert.equal(expirations(), 0)
})

test('missing access token restores cookie session; explicit logout prevents automatic restoration', async () => {
  const { session, storage, calls } = setup(null)
  assert.equal(await session.ensureAccess(), fresh)
  await session.logout()
  assert.equal(storage.getItem('token'), null)
  const reopened = setup(null, undefined, storage)
  assert.equal(await reopened.session.ensureAccess(), null)
  assert.equal(reopened.calls.length, 0)
  assert.deepEqual(calls.map(c => c.action), ['refresh', 'logout'])
})

test('failed logout retains current session so user can retry revocation', async () => {
  const { session, storage } = setup(fresh, async () => { throw failure(503) })
  await assert.rejects(session.logout())
  assert.equal(storage.getItem('token'), fresh)
  assert.equal(session.signedOut(), false)
})

test('late renewal never resurrects a session explicitly cleared in another tab', async () => {
  const gate = defer(), started = defer()
  const { session, storage } = setup(old, async () => { started.resolve(); return gate.promise })
  const pending = session.ensureAccess()
  await started.promise; session.invalidate(old)
  gate.resolve({ data: { access_token: fresh } })
  await assert.rejects(pending, { code: 'SESSION_CHANGED' })
  assert.equal(storage.getItem('token'), null)
})

test('late renewal cannot overwrite another account or send its pending draft', async () => {
  const gate = defer(), started = defer()
  const { session, storage } = setup(old, async () => { started.resolve(); return gate.promise })
  let writes = 0
  const { client } = http(session, async config => { writes++; return success(config) })
  const pending = client.post('/todo', { title: 'private' }, { expectedUserId: 1 })
  await started.promise
  const other = token({ sub: '2', sid: 'other' }); storage.setItem('token', other)
  gate.resolve({ data: { access_token: fresh } })
  await assert.rejects(pending, { code: 'SESSION_CHANGED' })
  assert.equal(storage.getItem('token'), other); assert.equal(writes, 0)
})

test('draft owner is checked before renewal or sending, even when other account has a valid token', async () => {
  const { session, calls } = setup(token({ sub: '2', sid: 'other' }))
  const { client } = http(session, () => assert.fail('must not send'))
  await assert.rejects(client.post('/todo', {}, { expectedUserId: 1 }), /账号已在其他窗口改变/)
  assert.equal(calls.length, 0)
})

test('stale 401 can use an already-renewed token but cannot expire a newer login', async () => {
  const { session, storage, calls } = setup(old)
  storage.setItem('token', fresh)
  assert.equal(await session.ensureAccess({ force: true, expectedToken: old }), fresh)
  assert.equal(calls.length, 0)
  const other = token({ sub: '2', sid: 'two' }); storage.setItem('token', other)
  await assert.rejects(session.ensureAccess({ force: true, expectedToken: old }), { code: 'SESSION_CHANGED' })
  assert.equal(session.invalidate(old), false); assert.equal(storage.getItem('token'), other)
})

test('two tabs sharing a Web Lock converge on one renewed access token', async () => {
  let queue = Promise.resolve()
  const locks = { request: (_, fn) => { const next = queue.then(fn); queue = next.catch(() => {}); return next } }
  const disk = memory({ token: old })
  const a = setup(null, undefined, disk, locks), b = setup(null, undefined, disk, locks)
  assert.deepEqual(await Promise.all([a.session.ensureAccess(), b.session.ensureAccess()]), [fresh, fresh])
  assert.equal(a.calls.length + b.calls.length, 1)
})

test('denied Web Locks uses local queue without retrying a failed auth HTTP request', async () => {
  const locks = { request() { throw Object.assign(new Error('denied'), { name: 'SecurityError' }) } }
  const { session, calls } = setup(old, async () => { throw failure(503) }, memory(), locks)
  await assert.rejects(session.ensureAccess())
  assert.equal(calls.length, 1)
})

test('queued logout follows renewal and leaves no renewable local session', async () => {
  const { session, calls } = setup(old)
  await Promise.all([session.ensureAccess(), session.logout()])
  assert.deepEqual(calls.map(c => c.action), ['refresh', 'logout'])
  assert.equal(session.getToken(), null); assert.equal(session.signedOut(), true)
})
