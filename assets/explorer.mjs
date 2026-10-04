import { matchesTopic, chronological } from './explorer-core.mjs';

const controls = document.querySelector('.explorer-controls');
const search = document.querySelector('#topic-search');
const order = document.querySelector('#topic-order');
const status = document.querySelector('#results-status');
const empty = document.querySelector('#no-results');
const groups = [...document.querySelectorAll('#topic-results > .topic-section:not(#chronological)')];
const timeline = document.querySelector('#chronological');
const timelineList = document.querySelector('#chronological-list');
const items = [...document.querySelectorAll('.card')].map((node, index) => ({
  node, index, parent: node.parentElement, category: node.dataset.category,
  seconds: Number(node.dataset.seconds),
  text: [...node.querySelectorAll('h3, .topic-body > p, .topic-body > ul, .source-details')].map(el => el.textContent).join(' ')
}));
const sorted = chronological(items);
let category = 'all';
let inputTimer;
function update() {
  let count = 0;
  for (const item of items) {
    item.node.hidden = !matchesTopic(item, search.value, category);
    if (!item.node.hidden) count++;
  }
  const byTime = order.value === 'time';
  if (byTime) {
    for (const item of sorted) timelineList.append(item.node);
  } else {
    for (const item of items) item.parent.append(item.node);
  }
  for (const group of groups) group.hidden = byTime || !items.some(item => item.parent === group && !item.node.hidden);
  timeline.hidden = !byTime || count === 0;
  document.querySelector('.category-links').hidden = byTime;
  status.textContent = `${count} sujet${count > 1 ? 's' : ''} affiché${count > 1 ? 's' : ''} sur ${items.length}.`;
  empty.hidden = count !== 0;
}
controls.hidden = false;
search.addEventListener('input', () => {
  clearTimeout(inputTimer);
  inputTimer = setTimeout(update, 180);
});
controls.addEventListener('change', event => {
  clearTimeout(inputTimer);
  if (event.target.name === 'category') category = event.target.value;
  update();
});
document.querySelector('#clear-search').addEventListener('click', () => {
  clearTimeout(inputTimer);
  search.value = ''; category = 'all';
  controls.querySelector('input[value="all"]').checked = true;
  update(); search.focus();
});
function revealHash() {
  const id = location.hash.slice(1);
  const item = items.find(item => item.node.id === id);
  const group = groups.find(group => group.id === id);
  if (!item && !group) return;
  clearTimeout(inputTimer);
  search.value = ''; category = 'all';
  controls.querySelector('input[value="all"]').checked = true;
  if (group) order.value = 'category';
  update();
  requestAnimationFrame(() => {
    const target = item?.node || group;
    target.scrollIntoView({block: 'start'});
    if (item) target.focus({preventScroll: true});
  });
}
window.addEventListener('hashchange', revealHash);
// Repeated clicks on an already active hash must also reveal a filtered entry.
document.addEventListener('click', event => {
  const link = event.target.closest('a[href^="#"]');
  if (link && link.hash === location.hash) revealHash();
});
update(); revealHash();

const shareStatus = document.querySelector('#share-status');
for (const item of items) {
  const button = item.node.querySelector('.copy-link');
  button.hidden = false;
  button.addEventListener('click', async () => {
    const url = new URL(location.href); url.hash = item.node.id;
    shareStatus.textContent = '';
    try {
      if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(url.href);
      button.textContent = 'Lien copié';
      shareStatus.textContent = `Lien copié pour : ${item.node.querySelector('h3').textContent}.`;
      setTimeout(() => { button.textContent = 'Copier le lien'; }, 2400);
    } catch {
      shareStatus.textContent = 'Copie non autorisée : utilisez « Lien du sujet », puis copiez son adresse depuis le navigateur.';
      button.textContent = 'Utiliser le lien du sujet';
    }
  });
}

const navLinks = [...document.querySelectorAll('nav a')];
function setCurrent(id) {
  for (const link of navLinks) {
    if (link.hash === `#${id}`) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  }
}
if ('IntersectionObserver' in window) {
  const visible = new Set();
  const sections = [...document.querySelectorAll('main > section')];
  const observer = new IntersectionObserver(entries => {
    for (const entry of entries) {
      if (entry.isIntersecting) visible.add(entry.target);
      else visible.delete(entry.target);
    }
    const current = sections.filter(section => visible.has(section) && section.getBoundingClientRect().top <= 140).at(-1)
      || sections.find(section => visible.has(section));
    const id = current?.id === 'version' ? 'excerpt' : current?.id;
    setCurrent(id);
  }, {rootMargin: '-110px 0px -40% 0px'});
  sections.forEach(section => observer.observe(section));
}
const printButton = document.querySelector('#print-presentation');
printButton.hidden = false;
printButton.addEventListener('click', () => {
  document.body.classList.add('print-presentation');
  window.print();
});
window.addEventListener('afterprint', () => document.body.classList.remove('print-presentation'));
