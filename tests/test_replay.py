import unittest
import json, tempfile, pathlib, math
from cdc_lab import replay as m

class Tests(unittest.TestCase):
    def test_record(self):
        r=m.encode_record('lab.curated',0,4,b'key',None)
        self.assertEqual(m.decode_record(r),(b'key',None))
        r=m.encode_record('lab.curated',0,5,None,b'{"a":1}')
        self.assertEqual(m.decode_record(r),(None,b'{"a":1}'))

