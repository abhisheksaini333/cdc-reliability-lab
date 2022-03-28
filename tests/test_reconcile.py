import unittest
import json, tempfile, pathlib, math
from cdc_lab import reconcile as m

class Tests(unittest.TestCase):
    def test_canonical(self):
        a=[{'id':'2','device_id':'3','value':'20.25','unit':'C','site':'west'}]
        b=[{'id':2,'device_id':3,'reading_value':20.25,'unit':'C','site':'west','version':99}]
        self.assertEqual(m.canonical(a),m.canonical(b))

