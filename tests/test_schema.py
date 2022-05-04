import unittest
import json, tempfile, pathlib, math
from cdc_lab import schema as m

class Tests(unittest.TestCase):
    def test_pgtypes(self):
        self.assertEqual(m.normalize_types([{'column_name':'value','data_type':'double precision'}]),{'value':'double'})
        self.assertEqual(m.normalize_types([{'column_name':'id','data_type':'bigint'}]),{'id':'bigint'})

