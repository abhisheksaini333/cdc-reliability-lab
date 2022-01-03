import unittest
from cdc_lab import __version__
class Package(unittest.TestCase):
    def test_version(self):
        self.assertEqual(__version__, "0.1.0")
