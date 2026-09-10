"""Ephemeral credential-free npm CONNECT allowlist; never exposed to the model."""
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import select
import socket
import threading

def target(route):
    if route!='registry.npmjs.org:443':raise ValueError('NPM_REGISTRY_ONLY')
    return ('registry.npmjs.org',443)

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*_):pass
    def do_CONNECT(self):
        try:address=target(self.path)
        except ValueError:
            self.send_error(403,'NPM_REGISTRY_ONLY');return
        try:
            with socket.create_connection(address,timeout=20) as remote:
                self.send_response(200);self.end_headers()
                while True:
                    ready,_,_=select.select([self.connection,remote],[],[],30)
                    if not ready:break
                    for source in ready:
                        data=source.recv(65536)
                        if not data:return
                        (remote if source is self.connection else self.connection).sendall(data)
        except OSError:return
    def do_GET(self):self.send_error(403,'HTTPS_CONNECT_REQUIRED')
    do_POST=do_GET

@contextmanager
def serving():
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:yield 'http://127.0.0.1:'+str(server.server_port)
    finally:server.shutdown();server.server_close();thread.join(timeout=2)
