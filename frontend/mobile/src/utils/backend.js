import { apiBase, backendOrigin, resourceURL } from './urls.mjs'

const origin = backendOrigin(import.meta.env.VITE_API_BASE_URL || '')
export const apiBaseURL = apiBase(origin)
export const uploadURL = path => resourceURL(path, origin)
