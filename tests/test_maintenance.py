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

    def test_cdc03(self):
        from cdc_lab.reconcile import canonical
        base={'id':1,'device_id':2,'value':3,'unit':'C','site':'north'}
        for key in ('id','device_id'):
            for value in (1.7,True,0,-1,'1.7'):
                with self.assertRaises(ValueError):canonical([{**base,key:value}])
        self.assertEqual(canonical([{**base,'id':'1'}])[0]['id'],1)

    def test_cdc04(self):
        from cdc_lab.schema import normalize_types,preflight
        self.assertEqual(normalize_types(None),{})
        with patch('cdc_lab.schema.postgres',return_value='null'):
            with self.assertRaisesRegex(ValueError,'incompatible'):preflight()
        for rows in ({},[None],[{'column_name':'id'}]):
            with self.assertRaises(ValueError):normalize_types(rows)

    def test_cdc05(self):
        from cdc_lab.workload import insert_sql
        row={'id':1,'device_id':1,'value':3,'unit':'C'}
        with self.assertRaisesRegex(ValueError,'duplicate'):insert_sql([row,dict(row)])
        self.assertIn('(1,1,3',insert_sql([row]))

    def test_cdc06(self):
        from cdc_lab.replay import bundle,verify_bundle
        valid=bundle([],{})
        for field,value in [('format_version',True),('record_count',False),('records',{}),('sha256',7)]:
            with self.assertRaises(ValueError): verify_bundle({**valid,field:value})
        for value in ([],None,{}):
            with self.assertRaises(ValueError):verify_bundle(value)
        self.assertEqual(verify_bundle(valid),[])
