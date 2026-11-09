import { ref, watch, onBeforeUnmount } from 'vue'
import { createDraftBuffer } from '@/utils/drafts.mjs'
import { protectEditor } from '@/utils/editorProtection.mjs'

export function useTodoDraft(session, snapshot) {
  const status = ref(session.record.savedAt ? '草稿已保存在本机' : '输入后自动保存到本机')
  const storageError = ref(''), exportText = ref(''), completed = ref(false)
  const buffer = createDraftBuffer(session, snapshot)
  let timer
  function flush(force = false) {
    clearTimeout(timer)
    if (buffer.completed) return true
    try {
      buffer.flush(force === true)
      storageError.value = ''
      status.value = session.record.savedAt ? '草稿已保存在本机' : '输入后自动保存到本机'
      return true
    } catch {
      storageError.value = '草稿未能保存到本机。请复制或下载备份，再重试保存；暂时不要关闭页面。'
      status.value = '草稿保存失败'
      return false
    }
  }
  const stop = watch(snapshot, () => {
    if (completed.value) return
    status.value = '正在保存草稿…'
    clearTimeout(timer)
    timer = setTimeout(flush, 400)
  }, { deep: true, flush: 'sync' })
  const unprotect = protectEditor(flush)
  const visibility = () => { if (document.visibilityState === 'hidden') flush() }
  const beforeUnload = event => {
    if (!flush()) { event.preventDefault(); event.returnValue = '' }
  }
  window.addEventListener('beforeunload', beforeUnload)
  document.addEventListener('visibilitychange', visibility)
  // Lock fallback uses a separate key immediately so the original remains untouched.
  if (session.copied && session.record.savedAt) flush()
  function finish() {
    clearTimeout(timer)
    completed.value = true
    try { buffer.finish(); status.value = '事项已提交'; return true }
    catch { storageError.value = '事项已提交，但本机草稿清理失败。请勿再次提交这份草稿。'; return false }
  }
  function discard() {
    if (!window.confirm('确定丢弃这份草稿？此操作无法撤销。')) return false
    try { buffer.discard() }
    catch { storageError.value = '草稿删除失败，请重试。'; return false }
    completed.value = true
    clearTimeout(timer)
    return true
  }
  function backupText() {
    const form = snapshot()
    return `${form.title}\n\n${form.description}\n\n---\n表单备份：\n${JSON.stringify(form, null, 2)}`
  }
  async function copy() {
    const text = backupText()
    try { await navigator.clipboard.writeText(text); status.value = '已复制全文和表单信息' }
    catch { exportText.value = text; status.value = '请在下方选中并复制备份' }
  }
  function download() {
    const url = URL.createObjectURL(new Blob([backupText()], { type: 'text/plain;charset=utf-8' }))
    const link = document.createElement('a'); link.href = url; link.download = 'todo-draft.txt'; link.click()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  }
  onBeforeUnmount(() => {
    flush(); stop(); unprotect(); session.release()
    window.removeEventListener('beforeunload', beforeUnload)
    document.removeEventListener('visibilitychange', visibility)
  })
  return { status, storageError, exportText, completed, flush, finish, discard, copy, download }
}
