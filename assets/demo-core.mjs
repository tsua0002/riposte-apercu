// Pure synchronization helpers shared by the browser and Node tests.
export function cueIndexAt(cues, seconds) {
  if (!Number.isFinite(seconds)) return -1;
  return cues.findIndex(cue => seconds >= cue.start && seconds < cue.end);
}
export function rangeState(cues, seconds) {
  if (!cues.length || !Number.isFinite(seconds)) return 'unavailable';
  if (seconds < cues[0].start) return 'before';
  if (seconds >= cues[cues.length - 1].end) return 'after';
  return cueIndexAt(cues, seconds) < 0 ? 'gap' : 'inside';
}
export function clock(seconds) {
  if (!Number.isFinite(seconds)) return '00:00';
  const total = Math.max(0, Math.floor(seconds));
  return `${String(Math.floor(total / 60)).padStart(2, '0')}:${String(total % 60).padStart(2, '0')}`;
}
