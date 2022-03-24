import unittest
import json, tempfile, pathlib, math
from cdc_lab import projection as m

class Tests(unittest.TestCase):
    def test_deduplicate(self):
        es=[{'event_id':'a','version':1},{'event_id':'a','version':1},{'event_id':'b','version':2}]
        self.assertEqual(len(m.unique(es)),2)
        self.assertEqual(es[0]['event_id'],'a')

    def test_current(self):
        events=[{'event_id':'a','id':1,'version':1,'deleted':0},{'event_id':'b','id':1,'version':2,'deleted':0}]
        self.assertEqual(m.current(events)[0]['version'],2)
        self.assertEqual(m.current(list(reversed(events))),m.current(events))

