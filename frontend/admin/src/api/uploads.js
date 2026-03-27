import request from './request'

/**
 * 上传图片
 * @param {File|Blob} file  图片文件
 * @param {string} module   所属模块，如 'todo' / 'news' / 'general'
 * @returns Promise<{ url: string }>
 */
export function uploadImage(file, module = 'general') {
  const form = new FormData()
  form.append('file', file)
  return request.post(`/admin/uploads/images?module=${module}`, form)
}
