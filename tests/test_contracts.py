import unittest
import json, tempfile, pathlib, math
from cdc_lab import contracts as m

class Tests(unittest.TestCase):
    def test_unwrap(self):
        self.assertEqual(m.unwrap({"payload":{"op":"c"}}), {"op":"c"})
        self.assertEqual(m.unwrap({"op":"u"}), {"op":"u"})
        self.assertIsNone(m.unwrap(None))
        with self.assertRaises(ValueError): m.unwrap([])

    def test_operation(self):
        for op in ("r","c","u","d"): self.assertEqual(m.operation({"op":op}),op)
        with self.assertRaises(ValueError): m.operation({"op":"truncate"})

    def test_row(self):
        self.assertEqual(m.row({"op":"d","before":{"id":7},"after":None}),{"id":7})
        self.assertEqual(m.row({"op":"u","after":{"id":8}}),{"id":8})
        with self.assertRaises(ValueError): m.row({"op":"d","before":None})

    def test_lsn(self):
        self.assertEqual(m.sequence({"source":{"lsn":123}}),123)
        for bad in (-1,True,"123",None):
            with self.assertRaises(ValueError): m.sequence({"source":{"lsn":bad}})

    def test_identity(self):
        e={"op":"c","source":{"lsn":12,"name":"lab","schema":"public","table":"readings"},"after":{"id":1}}
        a=m.identity(e)
        self.assertEqual(a,m.identity(dict(e,ts_ms=999)))
        e["after"]["id"]=2
        self.assertNotEqual(a,m.identity(e))

    def test_quality(self):
        self.assertEqual(m.quality({"id":1,"device_id":2,"value":24.0,"unit":"C"}),[])
        self.assertIn("value_out_of_range",m.quality({"id":1,"device_id":2,"value":999,"unit":"C"}))
        self.assertIn("unsupported_unit",m.quality({"id":1,"device_id":2,"value":2,"unit":"K"}))

    def test_normalize(self):
        e={"op":"d","source":{"lsn":10},"before":{"id":1,"device_id":2,"value":20,"unit":"C"}}
        v=m.normalize(e,{2:{"site":"north"}})
        self.assertEqual((v["deleted"],v["site"],v["version"]),(1,"north",10))
        self.assertIsNone(m.normalize(None,{}))

