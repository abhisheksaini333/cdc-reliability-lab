import unittest, tempfile, pathlib, json, math, os
from unittest.mock import patch, Mock

class Maintenance(unittest.TestCase):

    def test_cdc01(self):
        from cdc_lab.contracts import sequence
        for value in (None, [], 'source'):
            with self.assertRaises(ValueError): sequence({'source':value})
        self.assertEqual(sequence({'source':{'lsn':10}}),10)
