// Hover, keyboard and touch access to contextual notes. No network requests.
const hints = [...document.querySelectorAll('.info-hint')];
let opened = null;
function close(hint) {
  hint.querySelector('.info-tooltip').hidden = true;
  hint.querySelector('.info-button').setAttribute('aria-expanded', 'false');
  delete hint.dataset.pinned;
  if (opened === hint) opened = null;
}
function position(hint) {
  const button = hint.querySelector('.info-button'), tip = hint.querySelector('.info-tooltip');
  const rect = button.getBoundingClientRect();
  tip.style.width = `${Math.min(420, window.innerWidth - 24)}px`;
  tip.style.left = `${Math.max(12, Math.min(rect.left, window.innerWidth - tip.offsetWidth - 12))}px`;
  const below = rect.bottom + 8;
  tip.style.top = `${Math.max(12, below + tip.offsetHeight <= window.innerHeight - 12 ? below : rect.top - tip.offsetHeight - 8)}px`;
}
function show(hint) {
  if (opened && opened !== hint) close(opened);
  hint.querySelector('.info-tooltip').hidden = false;
  hint.querySelector('.info-button').setAttribute('aria-expanded', 'true');
  opened = hint; position(hint);
}
for (const hint of hints) {
  hint.dataset.enhanced = 'true';
  close(hint);
  const button = hint.querySelector('.info-button');
  let leaveTimer;
  hint.addEventListener('pointerenter', event => {
    clearTimeout(leaveTimer);
    if (event.pointerType === 'mouse') show(hint);
  });
  hint.addEventListener('pointerleave', event => {
    if (event.pointerType === 'mouse' && !hint.contains(document.activeElement)) {
      leaveTimer = setTimeout(() => { if (opened === hint) close(hint); }, 180);
    }
  });
  button.addEventListener('focus', () => {
    if (button.matches(':focus-visible')) show(hint);
  });
  button.addEventListener('click', () => {
    clearTimeout(leaveTimer);
    if (opened === hint && hint.dataset.pinned === 'true') close(hint);
    else { show(hint); hint.dataset.pinned = 'true'; }
  });
  hint.addEventListener('focusout', event => {
    if (!hint.contains(event.relatedTarget)) close(hint);
  });
}
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && opened) close(opened);
});
document.addEventListener('pointerdown', event => {
  if (opened && !opened.contains(event.target)) close(opened);
});
window.addEventListener('resize', () => { if (opened) position(opened); });
window.addEventListener('scroll', () => { if (opened) position(opened); }, {passive: true});
