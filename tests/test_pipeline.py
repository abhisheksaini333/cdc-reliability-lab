import unittest
import json, tempfile, pathlib, math
from cdc_lab import pipeline as m

class Tests(unittest.TestCase):
    def test_render(self):
        sql=m.render_sql({'POSTGRES_PASSWORD':"a'b"})
        self.assertIn("'password'='a''b'",sql)
        self.assertIn('BEGIN STATEMENT SET',sql)
        self.assertNotIn('${POSTGRES_PASSWORD}',sql)

    def test_submission_failure(self):
        with self.assertRaises(RuntimeError):m.submission_id('[ERROR] Could not execute SQL statement')
        with self.assertRaises(RuntimeError):m.submission_id('Shutting down the session...')
        self.assertEqual(m.submission_id('Job ID: '+'a'*32),'a'*32)

    def test_single_job(self):
        self.assertIsNone(m.ensure_no_active_job({'jobs':[{'state':'CANCELED'}]}))
        with self.assertRaises(RuntimeError):m.ensure_no_active_job({'jobs':[{'state':'RUNNING'}]})
        with self.assertRaises(RuntimeError):m.ensure_no_active_job({'jobs':[{'state':'RESTARTING'}]})


    def test_actual_savepoint_uri(self):
        sql = m.render_sql({'POSTGRES_PASSWORD':'local'},'file:/state/savepoints/savepoint-abc')
        self.assertIn("file:///state/savepoints/savepoint-abc",sql)
        for bad in ('file:///state/savepoints/../../etc/passwd','file://remote/state/savepoints/a','file:///state/savepoints/a?x=1'):
            with self.assertRaises(ValueError):m.render_sql({'POSTGRES_PASSWORD':'local'},bad)
