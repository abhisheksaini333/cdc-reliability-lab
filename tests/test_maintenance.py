import unittest, tempfile, pathlib, json, math, os
from unittest.mock import patch, Mock

class Maintenance(unittest.TestCase):

    def test_cdc01(self):
        from cdc_lab.contracts import sequence
        for value in (None, [], 'source'):
            with self.assertRaises(ValueError): sequence({'source':value})
        self.assertEqual(sequence({'source':{'lsn':10}}),10)

    def test_cdc02(self):
        from cdc_lab.contracts import identity
        base={'op':'c','source':{'lsn':1},'after':{'id':1}}
        for value in ('a:b','',None,True,'a\n'):
            with self.assertRaises(ValueError): identity({**base,'source':{'lsn':1,'name':value}})
        self.assertEqual(identity(base),'lab:public:readings:1:c:1')
