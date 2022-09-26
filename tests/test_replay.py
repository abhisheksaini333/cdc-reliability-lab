import unittest
import json, tempfile, pathlib, math
from cdc_lab import replay as m

class Tests(unittest.TestCase):
    def test_record(self):
        r=m.encode_record('lab.curated',0,4,b'key',None)
        self.assertEqual(m.decode_record(r),(b'key',None))
        r=m.encode_record('lab.curated',0,5,None,b'{"a":1}')
        self.assertEqual(m.decode_record(r),(None,b'{"a":1}'))

    def test_bundle(self):
        rows=[m.encode_record('lab.curated',0,0,None,b'{}')]
        b=m.bundle(rows,{0:1})
        self.assertEqual(b['record_count'],1)
        self.assertEqual(m.verify_bundle(b),rows)
        b['records'][0]['offset']=9
        with self.assertRaises(ValueError):m.verify_bundle(b)

    def test_offsetvalidation(self):
        rows=[m.encode_record('lab.curated',0,0,None,b'{}'),m.encode_record('lab.curated',0,1,None,b'{}')]
        self.assertIsNone(m.validate_offsets(rows,{'0':2}))
        with self.assertRaises(ValueError):m.validate_offsets(rows,{'0':1})
        with self.assertRaises(ValueError):m.validate_offsets(list(reversed(rows)),{'0':2})

    def test_privatewrite(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/'events.json';v=m.bundle([],{});m.write_bundle(p,v)
            self.assertEqual(p.stat().st_mode&0o777,0o600)
            with self.assertRaises(FileExistsError):m.write_bundle(p,v)
            self.assertEqual(m.read_bundle(p),v)

    def test_group(self):
        a=m.replay_group('trial');b=m.replay_group('trial')
        self.assertNotEqual(a,b);self.assertTrue(a.startswith('cdc-replay-trial-'))
        with self.assertRaises(ValueError):m.replay_group('live/unsafe')

    def test_target(self):
        self.assertEqual(m.replay_target('lab.replay.one'),'lab.replay.one')
        self.assertEqual(m.replay_target('lab.curated'),'lab.curated')
        with self.assertRaises(ValueError):m.replay_target('connect-offsets')

    def test_headers(self):
        r=m.encode_with_headers('lab.curated',0,0,b'k',b'v',[('trace',b'abc'),('empty',None)])
        self.assertEqual(m.decode_headers(r),[('trace',b'abc'),('empty',None)])


    def test_all_headers_validated_before_publication(self):
        record=m.encode_record('lab.curated',0,0,None,b'{}')
        record['headers']=[['trace','not base64!']]
        with self.assertRaises(ValueError):m.validate_offsets([record],{'0':1})
        record['headers']=[[12,'YWJj']]
        with self.assertRaises(ValueError):m.validate_offsets([record],{'0':1})
