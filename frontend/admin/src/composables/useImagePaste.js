import { uploadImage } from '@/api/uploads'

/**
 * 剪贴板图片粘贴上传 composable
 *
 * @param {object} options
 * @param {string}   options.module    所属模块，如 'todo' / 'news'
 * @param {Function} options.getValue  () => string  — 获取当前文本框的值
 * @param {Function} options.setValue  (val: string) => void  — 设置文本框的值
 * @param {Function} options.getEl     () => HTMLTextAreaElement  — 获取文本框 DOM 元素
 *
 * @returns {{ handlePaste: (e: ClipboardEvent) => void }}
 */
export function useImagePaste({ module = 'general', getValue, setValue, getEl }) {
  async function handlePaste(e) {
    const items = Array.from(e.clipboardData?.items || [])
    const imageItem = items.find(item => item.type.startsWith('image/'))
    if (!imageItem) return

    e.preventDefault()

    const blob = imageItem.getAsFile()
    if (!blob) return

    // 在光标处插入占位文本
    const el = getEl()
    const start = el?.selectionStart ?? getValue().length
    const end   = el?.selectionEnd   ?? start
    const placeholder = '![上传中...]()'

    const before = getValue().slice(0, start)
    const after  = getValue().slice(end)
    setValue(before + placeholder + after)

    // 恢复光标到占位符之后
    if (el) {
      const pos = start + placeholder.length
      requestAnimationFrame(() => {
        el.selectionStart = pos
        el.selectionEnd   = pos
        el.focus()
      })
    }

    try {
      const { data } = await uploadImage(blob, module)
      const inserted = `![图片](${data.url})`
      const current  = getValue()
      setValue(current.replace(placeholder, inserted))
    } catch (err) {
      console.error('图片上传失败', err)
      // 移除占位符
      setValue(getValue().replace(placeholder, ''))
    }
  }

  return { handlePaste }
}
