import unittest
import json, tempfile, pathlib, math
from cdc_lab import reconcile as m

class Tests(unittest.TestCase):
    def test_canonical(self):
        a=[{'id':'2','device_id':'3','value':'20.25','unit':'C','site':'west'}]
        b=[{'id':2,'device_id':3,'reading_value':20.25,'unit':'C','site':'west','version':99}]
        self.assertEqual(m.canonical(a),m.canonical(b))

    def test_difference(self):
        a=[{'id':1,'device_id':1,'value':1,'unit':'C','site':'north'}]
        b=[dict(a[0],value=2),dict(a[0],id=3)]
        r=m.compare(a,b)
        self.assertEqual(r['changed'],[1]);self.assertEqual(r['extra'],[3]);self.assertFalse(r['equivalent'])

    def test_digest(self):
        a=[{'id':1,'device_id':1,'value':1,'unit':'C','site':'north'}]
        self.assertEqual(m.digest(a),m.digest(list(reversed(a))))
        self.assertNotEqual(m.digest(a),m.digest([dict(a[0],value=2)]))


    def test_nonfinite_served_value_is_a_validation_error(self):
        for value in (None, float('nan'), float('inf')):
            with self.assertRaises(ValueError):m.canonical([{'id':1,'device_id':1,'reading_value':value,'unit':'C','site':'north'}])
