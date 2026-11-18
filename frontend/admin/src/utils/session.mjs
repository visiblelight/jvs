export function tokenClaims(token) {
  try { return JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/'))) }
  catch { return {} }
}
export function sameSession(left, right) {
  const a = tokenClaims(left), b = tokenClaims(right)
  return !!a.sub && a.sub === b.sub && a.sid === b.sid && a.ver === b.ver
}
export function needsRenewal(token, now = Date.now()) {
  const { exp, iat, sid } = tokenClaims(token)
  if (!Number.isFinite(exp)) return true
  const lead = !sid ? 0 : Number.isFinite(iat) ? Math.min(300, Math.max(1, (exp - iat) / 10)) : 300
  return exp * 1000 <= now + lead * 1000
}
export const terminalAuthError = error => [401, 403, 409].includes(error.response?.status)
export function sessionChanged() {
  const error = new Error('登录账号已在其他页面改变，请重新打开页面；草稿已保留。')
  error.code = 'SESSION_CHANGED'
  return error
}

export function createSessionManager({ storage, transport, locks, scope = '', now = Date.now,
                                       randomId = () => crypto.randomUUID() }) {
  const epochKey = `jvs:auth:epoch:${scope}`, signedOutKey = `jvs:auth:signed-out:${scope}`
  let pending = null, queue = Promise.resolve()
  const getToken = () => storage.getItem('token')
  const epoch = () => storage.getItem(epochKey)
  const signedOut = () => storage.getItem(signedOutKey) === '1'
  function queued(work) {
    const result = queue.then(work, work)
    queue = result.catch(() => {})
    return result
  }
  function locked(work) {
    if (!locks?.request) return queued(work)
    let started = false
    return Promise.resolve().then(() => locks.request(`jvs:auth:${scope}`, () => {
      started = true
      return work()
    })).catch(error => {
      if (!started && ['SecurityError', 'NotSupportedError'].includes(error.name)) return queued(work)
      throw error
    })
  }
  function invalidate(expected = getToken()) {
    if (getToken() !== expected) return false
    storage.removeItem('token')
    storage.setItem(epochKey, randomId())
    storage.setItem(signedOutKey, '1')
    return true
  }
  function persist(token) {
    if (!tokenClaims(token).sub) throw new Error('服务器返回的登录信息无效')
    storage.setItem('token', token)
    storage.removeItem(signedOutKey)
    return token
  }
  async function ensureAccess({ force = false, expectedToken = getToken() } = {}) {
    if (!force && expectedToken === getToken() && !needsRenewal(expectedToken, now())) return expectedToken
    if (!pending) {
      const startEpoch = epoch(), startToken = expectedToken
      pending = locked(async () => {
        const current = getToken()
        if (epoch() !== startEpoch) throw sessionChanged()
        if (current !== startToken) {
          if (sameSession(current, startToken)) return current
          throw sessionChanged()
        }
        if (!current && signedOut()) return null
        if (!force && !needsRenewal(current, now())) return current
        const before = tokenClaims(current)
        const response = await transport('refresh', { session_id: before.sid || null, user_id: Number(before.sub) || null })
        if (epoch() !== startEpoch || getToken() !== current) throw sessionChanged()
        const token = response.data.access_token, after = tokenClaims(token)
        if (current && (before.sub !== after.sub || (before.sid && before.sid !== after.sid))) throw sessionChanged()
        return persist(token)
      }).finally(() => { pending = null })
    }
    const token = await pending
    if (expectedToken && token && !sameSession(token, expectedToken)) {
      const before = tokenClaims(expectedToken), after = tokenClaims(token)
      if (before.sid || before.sub !== after.sub) throw sessionChanged()
    }
    return token
  }
  async function login(username, password) {
    return locked(async () => {
      const started = randomId()
      storage.setItem(epochKey, started)
      const response = await transport('login', { username, password })
      if (epoch() !== started) throw sessionChanged()
      persist(response.data.access_token)
      return response
    })
  }
  async function logout() {
    return locked(async () => {
      const token = getToken(), started = epoch()
      await transport('logout', { session_id: tokenClaims(token).sid || null })
      if (epoch() !== started || getToken() !== token) throw sessionChanged()
      invalidate(token)
    })
  }
  return { getToken, ensureAccess, login, logout, invalidate, signedOut }
}
