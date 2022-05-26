import unittest
import json, tempfile, pathlib, math
from cdc_lab import pipeline as m

class Tests(unittest.TestCase):
    def test_render(self):
        sql=m.render_sql({'POSTGRES_PASSWORD':"a'b"})
        self.assertIn("'password'='a''b'",sql)
        self.assertIn('BEGIN STATEMENT SET',sql)
        self.assertNotIn('${POSTGRES_PASSWORD}',sql)

