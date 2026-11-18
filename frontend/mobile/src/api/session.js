import axios from 'axios'
import { apiBaseURL } from '@/utils/backend'
import { createSessionManager } from '@/utils/session.mjs'

// No business interceptors: refresh errors must never recursively refresh themselves.
const authRequest = axios.create({ baseURL: apiBaseURL, timeout: 10000, withCredentials: true,
  headers: { 'X-JVS-Session': '1' } })
export const session = createSessionManager({
  storage: localStorage, locks: navigator.locks, scope: apiBaseURL,
  transport: (action, body) => authRequest.post(`/admin/auth/${action}`, body),
})
