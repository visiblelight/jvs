export function backendOrigin(value = '') {
  if (!value) return ''
  const url = new URL(value)
  if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password || url.search || url.hash || !['','/'].includes(url.pathname)) {
    throw new Error('VITE_API_BASE_URL 必须是后端 origin，例如 https://api.example.com，不包含 /api')
  }
  return url.origin
}

export function apiBase(value = '') { return `${backendOrigin(value)}/api` }

export function resourceURL(path, origin = '') {
  return typeof path === 'string' && path.startsWith('/uploads/') ? `${backendOrigin(origin)}${path}` : path
}
