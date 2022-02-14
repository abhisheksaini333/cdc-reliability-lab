import unittest
import json, tempfile, pathlib, math
from cdc_lab import config as m

class Tests(unittest.TestCase):
    def test_localenv(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/".env"; m.create_env(p)
            text=p.read_text(); self.assertIn("POSTGRES_PASSWORD=",text)
            self.assertEqual(p.stat().st_mode & 0o777,0o600)
            with self.assertRaises(FileExistsError): m.create_env(p)

