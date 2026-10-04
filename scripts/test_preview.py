#!/usr/bin/env python3
"""Check public output without needing access to the private archive."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
import json
import unittest
ROOT = Path(__file__).resolve().parents[1]
class Parser(HTMLParser):
    def __init__(self):
        super().__init__(); self.tags=[]; self.attrs=[]; self.ids=[]
    def handle_starttag(self, tag, attrs):
        self.tags.append(tag);self.attrs.extend(attrs)
        self.ids.extend(v for k,v in attrs if k=='id')
class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html=(ROOT/'index.html').read_text()
        cls.p=Parser();cls.p.feed(cls.html)
        cls.data=json.loads((ROOT/'data/sources.json').read_text())
    def test_public_scope(self):
        self.assertEqual(len(self.data),129)
        self.assertEqual(sum(x['type']=='actualité' for x in self.data),56)
        self.assertEqual(sum(x['type']=='contexte' for x in self.data),59)
        self.assertEqual(sum(x['type']=='anecdote / promotion' for x in self.data),14)
        self.assertEqual(sum(x.startswith('topic-') and x[6:].isdigit() for x in self.p.ids),129)
        for forbidden in ['transcription.md','sous-titres.srt','sous-titres.vtt','.storage_key']:
            self.assertFalse((ROOT/'data'/forbidden).exists())
        for entry in self.data:
            self.assertNotIn('quote',entry);self.assertNotIn('mentions',entry)
            for source in entry['sources']:self.assertNotIn('evidence',source)
    def test_controlled_demo(self):
        for tag in ['iframe','video','audio','form','object','embed']:
            self.assertNotIn(tag,self.p.tags)
        self.assertFalse(any(k.startswith('on') for k,v in self.p.attrs))
        self.assertEqual(self.p.tags.count('script'),3)
        self.assertTrue(any(k=='src' and urlsplit(v).path=='assets/explorer.mjs' for k,v in self.p.attrs))
        self.assertTrue(any(k=='src' and urlsplit(v).path=='assets/hints.mjs' for k,v in self.p.attrs))
        self.assertEqual(sum(v=='info-tooltip' for k,v in self.p.attrs if k=='class'),1)
        self.assertEqual(sum(v=='editorial-note' for k,v in self.p.attrs if k=='class'),5)
        self.assertIn(('class','skip-link'),self.p.attrs)
        self.assertEqual(sum(v=='topic-body' for k,v in self.p.attrs if k=='class'),129)
        self.assertIn("font-src 'self'",self.html)
        self.assertIn(('class','fingerprint'),self.p.attrs)
        self.assertEqual(sum(v=='source-details' for k,v in self.p.attrs if k=='class'),129)
        self.assertTrue(any(k=='src' and urlsplit(v).path=='assets/youtube-demo.mjs' for k,v in self.p.attrs))
        self.assertIn("default-src 'none'",self.html)
        self.assertIn("frame-src https://www.youtube-nocookie.com",self.html)
        self.assertNotIn("'unsafe-inline'",self.html)
        self.assertNotIn("'unsafe-eval'",self.html)
        starts=[float(v) for k,v in self.p.attrs if k=='data-start']
        ends=[float(v) for k,v in self.p.attrs if k=='data-end']
        self.assertEqual(len(starts),5)
        self.assertTrue(all(42 <= a < b < 52 for a,b in zip(starts,ends)))
        self.assertIn('Rigole !',self.html)
        self.assertNotIn('>Rire !<',self.html)
        self.assertIn('YouTube n’est contacté qu’après activation',self.html)
    def test_exploration(self):
        for id in ['topic-search','topic-order','clear-search','results-status','no-results','presentation','print-presentation','chronological']:
            self.assertIn(id,self.p.ids)
        self.assertEqual(sum(k=='data-category' for k,v in self.p.attrs),129)
        self.assertEqual(sum(k=='data-seconds' for k,v in self.p.attrs),129)
        self.assertEqual(sum(v=='copy-link' for k,v in self.p.attrs if k=='class'),129)
        self.assertEqual(sum(v=='permalink' for k,v in self.p.attrs if k=='class'),129)

    def test_editorial_copy(self):
        copy=json.loads((ROOT/'data/editorial-copy.json').read_text())
        review=(ROOT/'data/revue-de-presse.md').read_text()
        self.assertEqual(len(copy),len(self.data))
        for number,(expected,item) in enumerate(zip(copy,self.data),1):
            self.assertEqual(expected['id'],f'topic-{number}')
            self.assertEqual(expected['seconds'],item['seconds'])
            for field in ['title','summary','notes']:
                self.assertEqual(expected[field],item[field])
                self.assertIn(item[field],review)
        self.assertNotIn('fetch HTTP',self.html)
        self.assertNotIn('LLM',self.html)
        self.assertIn('3\u202f203 segments',self.html)
        self.assertIn('156\u202f693 octets',self.html)
        self.assertIn('Les gains de temps et la fiabilité restent à évaluer.',self.html)

    def test_back_to_top(self):
        class BackLink(HTMLParser):
            attrs=None
            def handle_starttag(self,tag,attrs):
                if tag=='a' and dict(attrs).get('class')=='back-to-top':
                    self.attrs=dict(attrs)
        link=BackLink();link.feed(self.html)
        self.assertEqual(link.attrs['href'],'#top')
        self.assertIn('hidden',link.attrs)
        self.assertIn('top',self.p.ids)

    def test_links(self):
        self.assertEqual(len(self.p.ids),len(set(self.p.ids)))
        for key,value in self.p.attrs:
            if key not in ('href','src'):continue
            if value.startswith('#'):self.assertIn(value[1:],self.p.ids)
            elif urlsplit(value).scheme:self.assertIn(urlsplit(value).scheme,['http','https','mailto'])
            else:self.assertTrue((ROOT/urlsplit(value).path).is_file(),value)
    def test_privacy_and_commitment(self):
        self.assertEqual(self.html.count('Su'+'au'),1)
        self.assertIn('<span class="print-surname"> Su'+'au</span>',self.html)
        css=(ROOT/'assets/style.css').read_text()
        self.assertIn('.print-surname{display:none}',css)
        self.assertIn('@media print{.print-surname{display:inline}',css)
        metadata=json.loads((ROOT/'data/version-transcription.json').read_text())
        self.assertEqual(metadata['segments'],3203)
        self.assertRegex(metadata['sha256'],r'^[a-f0-9]{64}$')
        self.assertIn(metadata['sha256'],self.html)
if __name__=='__main__':unittest.main()
