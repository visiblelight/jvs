import { computed, reactive, ref, toRef } from 'vue'
import { createItem, updateItem, getItem } from '@/api/todo'
import { localInputToISO } from '@/utils/datetime.mjs'
import { itemVersionMatches } from '@/utils/drafts.mjs'
import { useTodoDraft } from '@/composables/useTodoDraft'

export function useTodoEditor(session, emit) {
  const form = reactive(JSON.parse(JSON.stringify(session.record.form)))
  const hasScheduled = toRef(form, 'hasScheduled')
  const itemId = ref(session.record.itemId)
  const isEdit = computed(() => itemId.value !== null)
  const saving = ref(false), error = ref(session.problem || '')
  const draft = useTodoDraft(session, () => ({ ...form, tag_ids: [...form.tag_ids] }))

  function toggleScheduled() {
    hasScheduled.value = !hasScheduled.value
    if (!hasScheduled.value) form.scheduled_at = ''
    else { form.scheduled_at = form.due_date || ''; form.due_date = '' }
  }
  function close() { if (!saving.value && draft.flush()) emit('close') }
  function discard() { if (!saving.value && draft.discard()) emit('close') }
  function saveAsNew() {
    if (saving.value || draft.completed.value) return
    itemId.value = null
    session.record.itemId = null
    session.record.baseUpdatedAt = null
    form.status = 'pending'
    error.value = ''
    draft.flush(true)
  }
  async function handleSubmit() {
    if (saving.value || draft.completed.value) return
    error.value = ''
    if (!form.title.trim()) { error.value = '请填写事项标题'; return }
    if (hasScheduled.value && !form.scheduled_at) { error.value = '请填写执行时间'; return }
    if (!draft.flush(true)) return
    saving.value = true
    const config = { expectedUserId: session.ownerId }
    try {
      if (isEdit.value) {
        const { data } = await getItem(itemId.value, config)
        if (!itemVersionMatches(session.record, data)) {
          error.value = '原事项已被修改或删除。草稿已保留，请核对最新内容，或另存为新事项。'
          return
        }
      }
      const scheduled = hasScheduled.value ? localInputToISO(form.scheduled_at) : null
      const payload = {
        title: form.title.trim(), description: form.description || null,
        priority: form.priority, importance: form.importance, category_id: form.category_id,
        scheduled_at: scheduled,
        due_date: hasScheduled.value ? scheduled : localInputToISO(form.due_date),
        tag_ids: [...form.tag_ids],
      }
      if (isEdit.value) await updateItem(itemId.value, { ...payload, status: form.status }, config)
      else await createItem(payload, config)
      if (draft.finish()) emit('saved')
    } catch (e) {
      const detail = e.response?.data?.detail
      if (e.response?.status === 401) error.value = '登录已过期，草稿已保留。请重新登录后继续。'
      else if (e.response?.status === 404 && isEdit.value) error.value = '原事项已不存在或无权访问，草稿已保留。可以另存为新事项。'
      else if (e.code === 'ECONNABORTED' || e.code === 'ERR_NETWORK') error.value = '提交结果暂未确认，草稿已保留。请先检查事项列表，再决定是否重试。'
      else error.value = typeof detail === 'string' ? detail : (e.response ? '保存失败，草稿已保留，请检查填写内容后重试。' : e.message || '保存失败，草稿已保留。')
    } finally { saving.value = false }
  }
  return { form, hasScheduled, isEdit, saving, error, draft, toggleScheduled, close, discard, saveAsNew, handleSubmit }
}
