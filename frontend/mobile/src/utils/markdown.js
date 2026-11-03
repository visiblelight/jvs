import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { uploadURL } from './backend'

export function renderMarkdown(text) {
  if (!text) return ''
  const fragment = DOMPurify.sanitize(marked.parse(text, { breaks: true }), { RETURN_DOM_FRAGMENT: true })
  for (const image of fragment.querySelectorAll('img[src]')) {
    image.setAttribute('src', uploadURL(image.getAttribute('src')))
  }
  const container = document.createElement('div')
  container.append(fragment)
  return container.innerHTML
}
