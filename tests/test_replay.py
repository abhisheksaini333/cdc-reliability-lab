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

