import unittest
import json, tempfile, pathlib, math
from cdc_lab import metrics as m

class Tests(unittest.TestCase):
    def test_lag(self):
        self.assertEqual(m.partition_lag({0:20,1:8},{0:15,1:8}),{0:5,1:0})
        with self.assertRaises(ValueError):m.partition_lag({0:3},{0:5})

    def test_quality(self):
        self.assertEqual(m.quality_summary(90,10,120)['valid_ratio'],0.9)
        self.assertEqual(m.quality_summary(0,0,0)['valid_ratio'],None)
        with self.assertRaises(ValueError):m.quality_summary(3,-1,4)

