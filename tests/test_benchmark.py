import unittest
from cdc_lab.benchmark import measure
class Benchmark(unittest.TestCase):
    def test_invalid_limits_do_not_contact_services(self):
        for count,rounds in [(0,1),(100,0),(10001,1),(100,21)]:
            with self.assertRaises(ValueError):measure(count,rounds)
