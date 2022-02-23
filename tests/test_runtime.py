import unittest
import json, tempfile, pathlib, math
from cdc_lab import runtime as m

class Tests(unittest.TestCase):
    def test_command(self):
        r=m.command(["python3","-c","print('ready')"])
        self.assertEqual(r,"ready\n")
        with self.assertRaises(RuntimeError):m.command(["python3","-c","raise SystemExit(2)"])

    def test_http(self):
        from http.server import HTTPServer,BaseHTTPRequestHandler
        import threading
        class H(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200);self.end_headers();self.wfile.write(b'{"ok":true}')
            def log_message(self,*args):pass
        server=HTTPServer(("127.0.0.1",0),H);t=threading.Thread(target=server.serve_forever);t.start()
        try:self.assertEqual(m.http_json("http://127.0.0.1:%s"%server.server_port),{"ok":True})
        finally:server.shutdown();t.join();server.server_close()

    def test_wait(self):
        attempts=[]
        def test():
            attempts.append(1);return len(attempts)>2
        self.assertTrue(m.wait_for(test,timeout=1,interval=0.001))
        with self.assertRaises(TimeoutError):m.wait_for(lambda:False,timeout=0.01,interval=0.001)

    def test_sqlquote(self):
        self.assertEqual(m.sql_literal("O'Reilly"),"'O''Reilly'")
        self.assertEqual(m.sql_literal(12),"12")
        self.assertEqual(m.sql_literal(None),"NULL")
        with self.assertRaises(ValueError):m.sql_literal(float('nan'))

    def test_connector(self):
        from cdc_lab.config import create_env
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/'.env';create_env(p)
            result=m.connector_config(p)
            self.assertEqual(result['name'],'lab-source')
            self.assertNotIn('${',result['config']['database.password'])

    def test_topicnames(self):
        self.assertEqual(m.validate_topic('lab.public.readings'),'lab.public.readings')
        for bad in ('../x','x;id','', 'x'*250):
            with self.assertRaises(ValueError):m.validate_topic(bad)

