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

    def test_cdc07(self):
        from cdc_lab.replay import validate_offsets
        for bounds in ({'0':True},{'01':2},{'-1':2},{'0':-1},{'0':2**63},{0:1},[]):
            with self.assertRaises(ValueError):validate_offsets([],bounds)
        validate_offsets([],{'0':0,'1':5})

    def test_cdc08(self):
        from cdc_lab.replay import decode_record,decode_headers
        for value in (True,7,[],{},'@invalid'):
            with self.assertRaises(ValueError):decode_record({'key':value,'value':None})
            with self.assertRaises(ValueError):decode_headers({'headers':[['key',value]]})
        with self.assertRaises(ValueError):decode_record({})
        self.assertEqual(decode_record({'key':'eA==','value':None}),(b'x',None))

    def test_cdc09(self):
        from cdc_lab.replay import bundle,write_bundle
        with tempfile.TemporaryDirectory() as d:
            target=pathlib.Path(d)/'archive.json'
            with patch('cdc_lab.replay.os.fsync',side_effect=OSError('disk unavailable')):
                with self.assertRaises(OSError):write_bundle(target,bundle([],{}))
            self.assertFalse(target.exists())
            target.write_text('preserved')
            with self.assertRaises(FileExistsError):write_bundle(target,bundle([],{}))
            self.assertEqual(target.read_text(),'preserved')

    def test_cdc10(self):
        from cdc_lab.replay import export_topic
        with patch('kafka.KafkaConsumer') as consumer:
            for timeout in (0,-1,True,float('nan'),float('inf'),601):
                with self.assertRaisesRegex(ValueError,'deadline'):export_topic('lab.readings',timeout=timeout)
            consumer.assert_not_called()

    def test_cdc11(self):
        from cdc_lab.metrics import partition_lag
        with self.assertRaises(ValueError):partition_lag({0:10},{0:5,1:2})
        self.assertEqual(partition_lag({0:10,1:8},{0:7}),{0:3,1:8})

    def test_cdc12(self):
        from cdc_lab.metrics import percentile,throughput
        for samples,q in [([True],.5),([1],True),([1],'x'),([1],float('nan')),([None],.5)]:
            with self.assertRaises(ValueError):percentile(samples,q)
        for duration in (True,None,'1',float('inf')):
            with self.assertRaises(ValueError):throughput(1,duration)
        self.assertEqual(percentile([1,2,3],.5),2)
        self.assertEqual(throughput(3,1.5),2)

    def test_cdc13(self):
        from cdc_lab.runtime import wait_for
        for options in ({'timeout':0},{'timeout':float('nan')},{'interval':0},{'interval':True},{'interval':float('inf')}):
            predicate=Mock(return_value=True)
            with self.assertRaises(ValueError):wait_for(predicate,**options)
            predicate.assert_not_called()
        self.assertEqual(wait_for(lambda:'ready',timeout=.05,interval=.01),'ready')

    def test_cdc14(self):
        from cdc_lab.runtime import clickhouse
        response=Mock();response.read.side_effect=lambda n:b'x'*min(n,16*1024*1024+1)
        context=Mock();context.__enter__=Mock(return_value=response);context.__exit__=Mock(return_value=False)
        with patch('cdc_lab.config.load_env',return_value={'CLICKHOUSE_PASSWORD':'local'}),patch('cdc_lab.runtime.urllib.request.urlopen',return_value=context):
            with self.assertRaisesRegex(ValueError,'16 MiB'):clickhouse('SELECT 1')
        context.__exit__.assert_called_once()

    def test_cdc15(self):
        from cdc_lab.operations import select_job,checkpoint_status
        for value in (None,{'jobs':None},{'jobs':[None]},{'jobs':[{'state':'RUNNING','jid':'../x'}]}):
            with self.assertRaises(RuntimeError):select_job(value)
        with patch('cdc_lab.operations.runtime.http_json') as request:
            with self.assertRaises(RuntimeError):checkpoint_status('../x')
            request.assert_not_called()
        self.assertEqual(select_job({'jobs':[{'state':'RUNNING','jid':'a'*32}]}),'a'*32)

    def test_cdc16(self):
        from cdc_lab.operations import checkpoint_complete
        for count in (True,'2',-1,None):
            with self.assertRaises(ValueError):checkpoint_complete({'counts':{'completed':count}})
        with self.assertRaises(ValueError):checkpoint_complete({'counts':None})
        self.assertFalse(checkpoint_complete({'counts':{'completed':0}}))
        self.assertTrue(checkpoint_complete({'counts':{'completed':1}}))

    def test_cdc17(self):
        from cdc_lab.operations import savepoint_result
        for value in (None,{'status':None},{'status':{'id':'FAILED'}},{'status':{'id':'COMPLETED'},'operation':{'location':7}},{'status':{'id':'COMPLETED'},'operation':{'location':'http://wrong'}}):
            with self.assertRaises(RuntimeError):savepoint_result(value)
        self.assertIsNone(savepoint_result({'status':{'id':'IN_PROGRESS'}}))
        self.assertEqual(savepoint_result({'status':{'id':'COMPLETED'},'operation':{'location':'file:///state/savepoints/job'}}),'file:///state/savepoints/job')
