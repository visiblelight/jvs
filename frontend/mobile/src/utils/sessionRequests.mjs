import { terminalAuthError } from './session.mjs'
import { tokenUserId } from './editorProtection.mjs'

export function installSessionInterceptors(request, { session, expire }) {
  function checkOwner(config, token) {
    if (config.expectedUserId && token && tokenUserId(token) !== config.expectedUserId) {
      throw new Error('账号已在其他窗口改变，草稿已保留。请重新登录原账号后继续。')
    }
  }
  request.interceptors.request.use(async config => {
    const original = session.getToken()
    config._authToken = original
    checkOwner(config, original)
    let token
    try { token = await session.ensureAccess({ expectedToken: original }) }
    catch (error) {
      const failure = Object.assign(new Error(error.message), {
        response: error.response, code: error.code, config, _sessionFailure: true,
      })
      throw failure
    }
    checkOwner(config, token)
    config._authToken = token
    if (token) config.headers.Authorization = `Bearer ${token}`
    else delete config.headers.Authorization
    return config
  })
  request.interceptors.response.use(response => response, async error => {
    const config = error.config
    if (error._sessionFailure) {
      if (terminalAuthError(error)) await expire(error)
      return Promise.reject(error)
    }
    if (error.response?.status !== 401 || !config) return Promise.reject(error)
    if (!config._authRetried) {
      try {
        const token = await session.ensureAccess({ force: true, expectedToken: config._authToken })
        if (token) {
          checkOwner(config, token)
          config._authRetried = true
          return request(config)
        }
      } catch (refreshError) {
        if (!terminalAuthError(refreshError)) return Promise.reject(refreshError)
        await expire(error)
        return Promise.reject(refreshError)
      }
    }
    await expire(error)
    return Promise.reject(error)
  })
}
