import unittest
import json, tempfile, pathlib, math
from cdc_lab import operations as m

class Tests(unittest.TestCase):
    def test_jobselection(self):
        self.assertEqual(m.select_job({'jobs':[{'jid':'a','state':'RUNNING'}]}),'a')
        with self.assertRaises(RuntimeError):m.select_job({'jobs':[]})
        with self.assertRaises(RuntimeError):m.select_job({'jobs':[{'jid':'a','state':'RUNNING'},{'jid':'b','state':'RUNNING'}]})

    def test_checkpoints(self):
        self.assertTrue(m.checkpoint_complete({'counts':{'completed':2}}))
        self.assertFalse(m.checkpoint_complete({'counts':{'completed':0}}))

