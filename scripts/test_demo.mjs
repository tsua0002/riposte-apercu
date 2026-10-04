import {test} from 'node:test';
import assert from 'node:assert/strict';
import {cueIndexAt, rangeState, clock} from '../assets/demo-core.mjs';
const cues = [{start:42.04,end:44.2},{start:44.2,end:46.7},
  {start:46.7,end:49.22},{start:49.22,end:50.5},{start:51.3,end:51.82}];
test('selects the exact cue, including Rigole and boundaries', () => {
  assert.equal(cueIndexAt(cues,42.04),0);
  assert.equal(cueIndexAt(cues,44.2),1);
  assert.equal(cueIndexAt(cues,46.7),2);
  assert.equal(cueIndexAt(cues,49.22),3);
  assert.equal(cueIndexAt(cues,51.3),4);
});
test('no invented transcript before, after, or between cues', () => {
  for(const time of [0,42,50.5,51,51.82,3600,NaN]) assert.equal(cueIndexAt(cues,time),-1);
  assert.equal(rangeState(cues,0),'before');
  assert.equal(rangeState(cues,50.8),'gap');
  assert.equal(rangeState(cues,49.3),'inside');
  assert.equal(rangeState(cues,52),'after');
  assert.equal(rangeState([],42),'unavailable');
});
test('accessible playback time formatting', () => {
  assert.equal(clock(49.22),'00:49');
  assert.equal(clock(600),'10:00');
  assert.equal(clock(-1),'00:00');
  assert.equal(clock(NaN),'00:00');
});
