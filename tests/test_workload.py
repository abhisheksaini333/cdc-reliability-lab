import unittest
import json, tempfile, pathlib, math
from cdc_lab import workload as m

class Tests(unittest.TestCase):
    def test_inserts(self):
        rows=[{'id':1,'device_id':2,'value':20.5,'unit':"C'"}]
        s=m.insert_sql(rows)
        self.assertIn(chr(39)+'C'+chr(39)*3,s);self.assertIn('ON CONFLICT',s)
        with self.assertRaises(ValueError):m.insert_sql([])

    def test_updates(self):
        self.assertIn('WHERE id=3',m.update_sql(3,25))
        with self.assertRaises(ValueError):m.update_sql('3;DROP',2)

