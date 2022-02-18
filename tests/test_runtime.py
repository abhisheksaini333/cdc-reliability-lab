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

