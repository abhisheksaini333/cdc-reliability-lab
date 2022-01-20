import unittest
import json, tempfile, pathlib, math
from cdc_lab import fixtures as m

class Tests(unittest.TestCase):
    def test_devices(self):
        self.assertEqual(m.devices(3),m.devices(3))
        self.assertEqual([r["id"] for r in m.devices(3)],[1,2,3])
        with self.assertRaises(ValueError): m.devices(-1)

