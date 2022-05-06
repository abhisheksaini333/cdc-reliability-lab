import unittest
import json, tempfile, pathlib, math
from cdc_lab import metrics as m

class Tests(unittest.TestCase):
    def test_lag(self):
        self.assertEqual(m.partition_lag({0:20,1:8},{0:15,1:8}),{0:5,1:0})
        with self.assertRaises(ValueError):m.partition_lag({0:3},{0:5})

