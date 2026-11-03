import test from 'node:test'
import assert from 'node:assert/strict'
import { apiBase, resourceURL } from '../src/utils/urls.mjs'

test('same-origin and separated API/asset routing', () => {
  assert.equal(apiBase(), '/api')
  assert.equal(apiBase('https://api.example.com/'), 'https://api.example.com/api')
  assert.equal(resourceURL('/uploads/todo/a.png','https://api.example.com'), 'https://api.example.com/uploads/todo/a.png')
  assert.equal(resourceURL('/uploads/todo/a.png'), '/uploads/todo/a.png')
  assert.equal(resourceURL('https://external.example/image.png','https://api.example.com'), 'https://external.example/image.png')
  for (const input of ['https://api.example.com/api','javascript:alert(1)','https://user:secret@api.example.com','https://api.example.com/?token=secret']) assert.throws(() => apiBase(input))
})
