import {cueIndexAt, rangeState, clock} from './demo-core.mjs';

const rows = [...document.querySelectorAll('#demo-transcript .cue')];
const cues = rows.map(row => ({start: Number(row.dataset.start), end: Number(row.dataset.end)}));
const activate = document.querySelector('#demo-activate');
const reset = document.querySelector('#demo-reset');
const align = document.querySelector('#demo-align');
const follow = document.querySelector('#demo-follow');
const status = document.querySelector('#demo-status');
const syncStatus = document.querySelector('#demo-sync-status');
const transcript = document.querySelector('#demo-transcript');
const placeholder = document.querySelector('#demo-placeholder');
const timeLabel = document.querySelector('#demo-time');
let player = null, ready = false, active = -1, timer = null, loadTimer = null;
let followUntil = 0, lastRange = null, failed = false, disposed = false;

function message(text) { status.textContent = text; }
function setFollow(enabled) {
  follow.checked = enabled;
  syncStatus.textContent = enabled ? 'Suivi activé' : 'Suivi suspendu — Réaligner pour reprendre';
}
function highlight(index, force = false) {
  if (active !== index) {
    rows.forEach((row, i) => {
      row.classList.toggle('active', i === index);
      if (i === index) row.setAttribute('aria-current', 'true');
      else row.removeAttribute('aria-current');
    });
    active = index;
  }
  if (index < 0 || !follow.checked) return;
  const row = rows[index], r = row.getBoundingClientRect(), box = transcript.getBoundingClientRect();
  if (!force && r.top >= box.top + 6 && r.bottom <= box.bottom - 6) return;
  followUntil = Date.now() + 600;
  transcript.scrollTo({top: transcript.scrollTop + r.top - box.top - box.height / 2 + r.height / 2,
    behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth'});
}
function update(force = false) {
  if (!ready || failed || disposed) return;
  const seconds = player.getCurrentTime();
  timeLabel.textContent = clock(seconds);
  highlight(cueIndexAt(cues, seconds), force);
  const range = rangeState(cues, seconds);
  if (range !== lastRange) {
    lastRange = range;
    if (range === 'inside') message('Le texte suit le passage affiché.');
    else if (range === 'gap') message('Pause entre deux répliques de cet extrait.');
    else if (range === 'before') message('Le lecteur est avant l’extrait. Une publicité YouTube peut retarder le démarrage ; utilisez Relancer l’extrait quand la vidéo est prête.');
    else message('Transcription non affichée dans cette démonstration à cet endroit. Vous pouvez relancer l’extrait.');
  }
}
function fail(text) {
  if (disposed) return;
  failed = true;
  clearTimeout(loadTimer);
  if (timer) clearInterval(timer);
  activate.hidden = false;
  activate.disabled = false;
  activate.textContent = 'Réessayer de charger YouTube';
  reset.disabled = align.disabled = true;
  message(text + ' Le lien vers la vidéo officielle reste disponible.');
}
function startAt(seconds) {
  if (!ready || failed) return;
  setFollow(true); lastRange = null;
  player.seekTo(seconds, true);
  player.playVideo();
  highlight(cueIndexAt(cues, seconds), true);
  message('Lecture demandée. Si nécessaire, appuyez sur ▶ dans le lecteur YouTube.');
}
function createPlayer() {
  if (disposed || failed) return;
  player = new window.YT.Player('demo-mount', {
    host: 'https://www.youtube-nocookie.com',
    width: '100%', height: '100%', videoId: 'kKOcQM1eynE',
    playerVars: {playsinline: 1, controls: 1, start: Math.floor(cues[0].start),
      origin: window.location.origin, autoplay: 1},
    events: {
      onReady(event) {
        if (disposed || failed) return;
        clearTimeout(loadTimer); ready = true;
        placeholder.hidden = true; activate.hidden = true;
        reset.disabled = align.disabled = false;
        const iframe = event.target.getIframe();
        iframe.title = 'La Riposte — vidéo YouTube officielle';
        iframe.setAttribute('referrerpolicy', 'strict-origin-when-cross-origin');
        iframe.setAttribute('allow', 'autoplay; encrypted-media; picture-in-picture; fullscreen');
        iframe.setAttribute('allowfullscreen', '');
        document.querySelector('#demo-frame').setAttribute('aria-busy', 'false');
        timer = setInterval(() => update(), 200);
        startAt(cues[0].start);
      },
      onStateChange() { update(); },
      onError(event) {
        const errors = {100: 'La vidéo officielle est indisponible.',
          101: 'Le propriétaire interdit la lecture intégrée de cette vidéo.',
          150: 'Le propriétaire interdit la lecture intégrée de cette vidéo.',
          153: 'YouTube refuse l’identification de cette intégration.',
          2: 'YouTube refuse les paramètres de cette vidéo.',
          5: 'Ce navigateur ne peut pas lire la vidéo YouTube.'};
        fail(errors[event.data] || 'La lecture YouTube a rencontré une erreur.');
      }
    }
  });
}
function loadPlayer() {
  activate.disabled = true;
  failed = false; ready = false; lastRange = null;
  if (timer) clearInterval(timer);
  if (player) { player.destroy(); player = null; }
  // The API replaces its mounting node with an iframe; recreate it for retries.
  placeholder.hidden = false;
  document.querySelector('#demo-frame').setAttribute('aria-busy', 'true');
  document.querySelector('#demo-frame').replaceChildren();
  const node = document.createElement('div'); node.id = 'demo-mount';
  document.querySelector('#demo-frame').append(node);
  message('Connexion à YouTube et chargement du lecteur…');
  loadTimer = setTimeout(() => fail('YouTube n’a pas répondu. Vérifiez votre connexion ou votre bloqueur de contenus.'), 25000);
  if (window.YT?.Player) { createPlayer(); return; }
  window.onYouTubeIframeAPIReady = createPlayer;
  document.querySelector('#youtube-api')?.remove();
  const script = document.createElement('script');
  script.id = 'youtube-api'; script.src = 'https://www.youtube.com/iframe_api';
  script.async = true; script.onerror = () => fail('Le script YouTube n’a pas pu être chargé.');
  document.head.append(script);
}
activate.addEventListener('click', loadPlayer);
reset.addEventListener('click', () => startAt(cues[0].start));
align.addEventListener('click', () => { setFollow(true); update(true); });
follow.addEventListener('change', () => { setFollow(follow.checked); if (follow.checked) update(true); });
for (const event of ['wheel', 'touchmove']) {
  transcript.addEventListener(event, () => { if (ready) setFollow(false); }, {passive: true});
}
transcript.addEventListener('scroll', () => {
  if (ready && Date.now() > followUntil) setFollow(false);
}, {passive: true});
rows.forEach((row, i) => row.querySelector('a').addEventListener('click', event => {
  if (!ready || failed || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
  event.preventDefault(); startAt(cues[i].start);
}));
window.addEventListener('pagehide', event => {
  if (event.persisted) return;
  disposed = true; clearTimeout(loadTimer); clearInterval(timer);
  player?.destroy();
});
if (cues.length && cues.every(cue => Number.isFinite(cue.start) && cue.end > cue.start)) {
  activate.disabled = false;
} else message('Extrait indisponible ; utilisez le lien YouTube officiel.');
