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

    def test_deleted(self):
        a={'event_id':'a','id':1,'version':1,'deleted':0}
        b={'event_id':'b','id':1,'version':2,'deleted':1}
        self.assertEqual(m.delivery_counts([a,b,a]),{'a':2,'b':1})
        self.assertEqual(m.current([a,b,a]),[])
        self.assertEqual(m.current([a,dict(b,deleted=0,quality=['bad'])]),[])


    def test_latest_invalid_hides_stale_value(self):
        old = {"event_id":"a","id":1,"version":1,"quality":[],"deleted":0}
        invalid = dict(old,event_id="b",version=2,quality=["value_out_of_range"])
        restored = dict(old,event_id="c",version=3)
        self.assertEqual(m.current([old,invalid]),[])
        self.assertEqual(m.current([old,invalid,restored]),[restored])
