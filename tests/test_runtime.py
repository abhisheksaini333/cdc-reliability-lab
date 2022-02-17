import unittest
import json, tempfile, pathlib, math
from cdc_lab import runtime as m

class Tests(unittest.TestCase):
    def test_command(self):
        r=m.command(["python3","-c","print('ready')"])
        self.assertEqual(r,"ready\n")
        with self.assertRaises(RuntimeError):m.command(["python3","-c","raise SystemExit(2)"])

