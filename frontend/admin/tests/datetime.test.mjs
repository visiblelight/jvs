import test from 'node:test'
import assert from 'node:assert/strict'
import { parseInstant, parseDateKey, formatLocalDatetime, localInputToISO, timeAgo, businessDateKey, localDateKey } from '../src/utils/datetime.mjs'

for (const zone of ['UTC','Asia/Shanghai','America/New_York']) {
  test(`instant and input roundtrip in ${zone}`, () => {
    process.env.TZ = zone
    const instant = '2026-11-03T05:00:00Z'
    assert.equal(parseInstant('2026-11-03T05:00:00').getTime(), Date.parse(instant))
    assert.equal(parseInstant('2026-11-03T13:00:00+08:00').getTime(), Date.parse(instant))
    let input = formatLocalDatetime(instant)
    for (let i=0;i<2;i++) {
      const iso = localInputToISO(input)
      assert.equal(iso, '2026-11-03T05:00:00.000Z')
      input = formatLocalDatetime(iso)
    }
    assert.equal(timeAgo('2026-11-03T05:00:00', Date.parse(instant)), '刚刚')
    assert.equal(localDateKey(parseDateKey('2026-11-03')), '2026-11-03')
    assert.equal(Number.isNaN(parseInstant('2026-11-03').getTime()), true)
    assert.equal(businessDateKey(new Date('2026-11-03T16:00:00Z')), '2026-11-04')
  })
}

test('Shanghai display and DST invalid local input', () => {
  process.env.TZ='Asia/Shanghai'
  assert.equal(formatLocalDatetime('2026-11-03T05:00:00Z'), '2026-11-03T13:00')
  process.env.TZ='America/New_York'
  assert.throws(() => localInputToISO('2026-03-08T02:30'))
  assert.equal(Number.isNaN(parseDateKey('2026-02-30').getTime()), true)
  assert.equal(formatLocalDatetime(null),'')
})
