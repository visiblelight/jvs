import { reactive } from 'vue'

// 模块级单例，所有组件共享同一状态
const state = reactive({
  toasts: [],
  confirm: null, // { title, message, danger, resolve }
})

let _id = 0

export function useDialog() {
  /**
   * 显示 toast 通知
   * @param {string} message
   * @param {'error'|'success'|'info'} type
   */
  const toast = (message, type = 'error') => {
    const id = ++_id
    state.toasts.push({ id, message, type })
    setTimeout(() => {
      const idx = state.toasts.findIndex(t => t.id === id)
      if (idx !== -1) state.toasts.splice(idx, 1)
    }, 3800)
  }

  /**
   * 显示自定义确认弹窗，返回 Promise<boolean>
   * @param {string} message
   * @param {{ title?: string, danger?: boolean }} options
   */
  const confirm = (message, options = {}) => {
    const { title = '确认操作', danger = false } = typeof options === 'string'
      ? { title: options }
      : options
    return new Promise(resolve => {
      state.confirm = { title, message, danger, resolve }
    })
  }

  return { toast, confirm, _state: state }
}
