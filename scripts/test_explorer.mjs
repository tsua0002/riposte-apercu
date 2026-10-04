import test from 'node:test';
import assert from 'node:assert/strict';
import { normalize, matchesTopic, chronological, showBackToTop } from '../assets/explorer-core.mjs';
const topic = {category:'actualité',text:'Édouard Philippe — Retraites. Le Monde. Note : à vérifier.'};
test('case and accents do not impede search', () => {
  assert.equal(normalize('ÉDOUARD'), 'edouard');
  assert.equal(matchesTopic(topic,'EDOUARD retraites'),true);
  assert.equal(matchesTopic(topic,'   monde   '),true);
});
test('every word and category must match', () => {
  assert.equal(matchesTopic(topic,'retraites logement'),false);
  assert.equal(matchesTopic(topic,'','contexte'),false);
  assert.equal(matchesTopic(topic,'','actualité'),true);
  assert.equal(matchesTopic(topic,''),true);
});
test('search covers editorial notes without claiming verification', () => {
  assert.equal(matchesTopic(topic,'a verifier'),true);
});
test('Dati does not match validation, but word prefixes remain useful', () => {
  assert.equal(matchesTopic({category:'actualité',text:'Carcassonne : refus de suspendre, pas validation définitive.'},'Dati'),false);
  assert.equal(matchesTopic({category:'actualité',text:'Procès de Rachida Dati'},'dati'),true);
  assert.equal(matchesTopic(topic,'retraite'),true);
  assert.equal(matchesTopic(topic,'Édou'),true);
});
test('back-to-top stays quiet until a viewport has been passed', () => {
  assert.equal(showBackToTop(0,844),false);
  assert.equal(showBackToTop(200,844),false);
  assert.equal(showBackToTop(843,844),false);
  assert.equal(showBackToTop(844,844),true);
  assert.equal(showBackToTop(599,300),false);
  assert.equal(showBackToTop(600,300),true);
  assert.equal(showBackToTop(0,300),false);
});
test('chronological ordering is stable and does not mutate input', () => {
  const input = [{seconds:9,index:1},{seconds:2,index:2},{seconds:9,index:0}];
  assert.deepEqual(chronological(input).map(x=>x.index),[2,0,1]);
  assert.equal(input[0].index,1);
});
