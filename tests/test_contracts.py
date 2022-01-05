import unittest
import json, tempfile, pathlib, math
from cdc_lab import contracts as m

class Tests(unittest.TestCase):
    def test_unwrap(self):
        self.assertEqual(m.unwrap({"payload":{"op":"c"}}), {"op":"c"})
        self.assertEqual(m.unwrap({"op":"u"}), {"op":"u"})
        self.assertIsNone(m.unwrap(None))
        with self.assertRaises(ValueError): m.unwrap([])

