import unittest
import json, tempfile, pathlib, math
from cdc_lab import evidence as m

class Tests(unittest.TestCase):
    def test_journal(self):
        with tempfile.TemporaryDirectory() as d:
            folder=pathlib.Path(d)
            a=m.record_run(folder,[{'passed':False,'error':'TimeoutError'}])
            b=m.record_run(folder,[{'passed':True}])
            self.assertNotEqual(a,b)
            self.assertFalse(json.loads(a.read_text())[0]['passed'])
            self.assertEqual(a.stat().st_mode&0o777,0o600)

