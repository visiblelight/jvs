import test from 'node:test'
import assert from 'node:assert/strict'
import { periodKey, periodBounds, calendarLogDate, nextBusinessDayDelay, watchBusinessDay } from '../src/utils/tick.mjs'

test('period boundaries and late makeups independent of browser timezone', () => {
  for (const zone of ['UTC','Asia/Shanghai','America/New_York']) {
    process.env.TZ=zone
    assert.equal(periodKey('weekly','2025-12-29'),'2026-W01')
    assert.deepEqual(periodBounds('weekly','2026-W01'),['2025-12-29','2026-01-04'])
    assert.deepEqual(periodBounds('monthly','2024-02'),['2024-02-01','2024-02-29'])
    assert.equal(calendarLogDate({is_makeup:true,period_key:'2026-03-01',ticked_at:'2026-11-03T00:00:00Z'}),'2026-03-01')
    assert.equal(calendarLogDate({is_makeup:false,ticked_at:'2026-11-03T16:30:00Z'}),'2026-11-04')
  }
})

test('refresh at Shanghai midnight, visible recovery, failed retry and cleanup', async () => {
  let now=Date.parse('2026-11-03T15:59:59Z'), pending, delay, listener, calls=0, fail=false
  const env={
    now:()=>now, setTimeout:(fn,ms)=>{pending=fn;delay=ms;return 1}, clearTimeout:()=>{pending=null},
    document:{visibilityState:'visible',addEventListener:(_,fn)=>{listener=fn},removeEventListener:()=>{listener=null}},
    onError:()=>{},
  }
  const stop=watchBusinessDay(async()=>{calls++;if(fail)throw Error('retry')},()=> 'Asia/Shanghai',env)
  assert.equal(delay,1100)
  now+=1100;await pending();assert.equal(calls,1)
  assert.ok(delay>23*3600000)
  now+=86400000;fail=true;listener();await new Promise(resolve=>setImmediate(resolve))
  assert.equal(delay,60000)
  fail=false;await pending();assert.equal(calls,3)
  stop();assert.equal(listener,null);assert.equal(pending,null)
})

test('next midnight accounts for DST day lengths', () => {
  assert.equal(nextBusinessDayDelay(Date.parse('2026-03-08T05:00:00Z'),'America/New_York'),23*3600000+100)
  assert.equal(nextBusinessDayDelay(Date.parse('2026-11-01T04:00:00Z'),'America/New_York'),25*3600000+100)
})
