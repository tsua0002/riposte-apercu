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
        self.assertEqual(sum(x.startswith('topic-') for x in self.p.ids),129)
        for forbidden in ['transcription.md','sous-titres.srt','sous-titres.vtt','.storage_key']:
            self.assertFalse((ROOT/'data'/forbidden).exists())
        for entry in self.data:
            self.assertNotIn('quote',entry);self.assertNotIn('mentions',entry)
            for source in entry['sources']:self.assertNotIn('evidence',source)
    def test_no_active_content(self):
        for tag in ['script','iframe','video','audio','form','input','object','embed']:
            self.assertNotIn(tag,self.p.tags)
        self.assertFalse(any(k.startswith('on') for k,v in self.p.attrs))
        self.assertIn("default-src 'none'",self.html)
    def test_links(self):
        self.assertEqual(len(self.p.ids),len(set(self.p.ids)))
        for key,value in self.p.attrs:
            if key!='href':continue
            if value.startswith('#'):self.assertIn(value[1:],self.p.ids)
            elif urlsplit(value).scheme:self.assertIn(urlsplit(value).scheme,['http','https','mailto'])
            else:self.assertTrue((ROOT/value).is_file(),value)
    def test_privacy_and_commitment(self):
        for path in ROOT.rglob('*'):
            if path.is_file() and '.git' not in path.parts:
                self.assertNotIn('Su'+'au',path.read_text(errors='replace'),str(path))
        metadata=json.loads((ROOT/'data/version-transcription.json').read_text())
        self.assertEqual(metadata['segments'],3203)
        self.assertRegex(metadata['sha256'],r'^[a-f0-9]{64}$')
        self.assertIn(metadata['sha256'],self.html)
if __name__=='__main__':unittest.main()
