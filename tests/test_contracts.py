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

