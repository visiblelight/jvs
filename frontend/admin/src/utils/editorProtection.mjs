const editors = new Set()
export function protectEditor(flush) {
  editors.add(flush)
  return () => editors.delete(flush)
}
export function flushEditors() {
  let saved = true
  for (const flush of editors) {
    try { if (!flush()) saved = false } catch { saved = false }
  }
  return saved
}

export function safeReturnPath(value, fallback) {
  if (typeof value !== 'string' || !value.startsWith('/') || value.startsWith('//') || /[\\\r\n]/.test(value)) return fallback
  try {
    const url = new URL(value, 'https://jvs.invalid')
    if (url.origin !== 'https://jvs.invalid' || url.pathname === '/login') return fallback
    return url.pathname + url.search + url.hash
  } catch { return fallback }
}

// Only a local account-mismatch guard; the server still verifies authentication.
export function tokenUserId(token) {
  try {
    const part = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')
    return Number(JSON.parse(atob(part)).sub) || null
  } catch { return null }
}
export function isCurrentUnauthorized(requestToken, currentToken, url = '') {
  return !url.endsWith('/auth/login') && requestToken === currentToken
}

// Also give initial network/403 failures a usable login page instead of a blank route.
export function authFailureRedirect(requestToken, currentToken, returnTo, status) {
  if (currentToken && currentToken !== requestToken) return false
  return { path: '/login', query: { redirect: returnTo, ...(status === 401 ? { expired: '1' } : { retry: '1' }) } }
}
