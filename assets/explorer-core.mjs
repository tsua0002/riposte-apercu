// Pure helpers shared by the browser and tests. No network or storage.
export function normalize(value) {
  return String(value).normalize('NFD').replace(/\p{M}/gu, '').toLocaleLowerCase('fr').replace(/[’']/g, ' ');
}
export function matchesTopic(topic, query, category = 'all') {
  const words = value => normalize(value).split(/[^\p{L}\p{N}]+/gu).filter(Boolean);
  const contentWords = words(topic.text);
  return (category === 'all' || topic.category === category) &&
    words(query).every(word => contentWords.some(candidate => candidate.startsWith(word)));
}
export function chronological(topics) {
  return [...topics].sort((a, b) => a.seconds - b.seconds || a.index - b.index);
}
