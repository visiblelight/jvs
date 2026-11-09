import { ref, shallowRef, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { apiBaseURL } from '@/utils/backend'
import { createDraftStore, newDraftId, openDraft, initialTodoForm, itemVersionMatches } from '@/utils/drafts.mjs'
import { flushEditors } from '@/utils/editorProtection.mjs'
import { formatLocalDatetime } from '@/utils/datetime.mjs'
import { getItem } from '@/api/todo'

export function useTodoDrafts(appName) {
  const route = useRoute(), router = useRouter()
  const ownerId = useAuthStore().user.id
  const storage = {
    get length() { return localStorage.length }, key: i => localStorage.key(i),
    getItem: key => localStorage.getItem(key), setItem: (key, value) => localStorage.setItem(key, value),
    removeItem: key => localStorage.removeItem(key),
  }
  const store = createDraftStore(storage, `${apiBaseURL}:${appName}`, ownerId)
  const drafts = ref([]), draftError = ref(''), editor = shallowRef(null)
  let opening = false, disposed = false
  function refreshDrafts() {
    try {
      const result = store.list()
      drafts.value = result.items
      draftError.value = result.unreadable.length ? '有草稿无法读取，原始备份仍保留。' : ''
    } catch { draftError.value = '无法读取本机草稿，请检查浏览器存储设置。' }
  }
  async function openEditor(item = null, id = null) {
    if (opening || editor.value) return
    opening = true
    let session
    try {
      let record
      if (id) {
        record = store.read(id)
        if (!record) throw new Error('当前账号没有这份草稿。可在本机草稿列表中选择其他草稿。')
      } else {
        const form = initialTodoForm(item)
        form.scheduled_at = formatLocalDatetime(item?.scheduled_at)
        form.due_date = item?.scheduled_at ? '' : formatLocalDatetime(item?.due_date)
        record = { id: newDraftId(), itemId: item?.id ?? null, baseUpdatedAt: item?.updated_at ?? null, form, savedAt: null }
      }
      session = await openDraft(store, record, { locks: navigator.locks })
      record = session.record
      let problem = ''
      if (id && record.itemId) {
        try {
          item = (await getItem(record.itemId, { expectedUserId: ownerId })).data
          if (!itemVersionMatches(record, item)) problem = '原事项已有更新，草稿已保留；请核对最新内容，或另存为新事项。'
        }
        catch { problem = '暂时无法读取原事项，草稿已保留；可重试保存或另存为新事项。' }
      }
      if (disposed || route.path !== '/todo') { session.release(); return }
      editor.value = { ...session, item, problem, store, ownerId }
      await router.replace({ path: '/todo', query: { ...route.query, draft: session.record.id } })
    } catch (error) { session?.release(); draftError.value = error.message || '无法打开草稿' }
    finally { opening = false }
  }
  async function closeEditor() {
    if (!flushEditors()) return
    editor.value = null
    const query = { ...route.query }; delete query.draft
    await router.replace({ path: '/todo', query })
    refreshDrafts()
  }
  watch(() => route.query.draft, async id => {
    if (route.path !== '/todo' || opening || id === editor.value?.record.id) return
    editor.value = null
    await nextTick() // Release the previous editor's lock before restoring another.
    if (typeof id === 'string') openEditor(null, id)
  })
  onMounted(() => {
    refreshDrafts()
    window.addEventListener('storage', refreshDrafts)
    if (typeof route.query.draft === 'string') openEditor(null, route.query.draft)
  })
  onUnmounted(() => { disposed = true; window.removeEventListener('storage', refreshDrafts) })
  return { drafts, draftError, editor, openEditor, closeEditor, refreshDrafts }
}
