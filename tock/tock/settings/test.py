from django.utils.crypto import get_random_string

from .base import *  # noqa

SECRET_KEY = get_random_string(50)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'tock-test',
        'HOST': 'localhost',
    }
}

INSTALLED_APPS += ('nplusone.ext.django', )
MIDDLEWARE_CLASSES += ('nplusone.ext.django.NPlusOneMiddleware', )
NPLUSONE_RAISE = True

MEDIA_ROOT = './media/'

# Testing Float API endpoint.
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
import socket

class MockServerRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Process an HTTP GET request in various ways dependant on path
        requested."""

        if self.path == '/people':
            f = open('employees/fixtures/float_people_fixture.json').read()
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(f, 'UTF-8'))
        elif self.path == '/tasks':
            f = open('hours/fixtures/float_task_fixture.json').read()
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(f, 'UTF-8'))
        else:
            self.send_response(400)
            self.send_header("Content-type", "application/json")
            self.end_headers()

class TestMockServer(object):
    def run_server(port):
        # Configure mock server.
        mock_server_port = port
        mock_server = HTTPServer(('localhost', mock_server_port), MockServerRequestHandler)
        # Start running mock server in a separate thread.
        # Daemon threads automatically shut down when the main process exits.
        mock_server_thread = Thread(target=mock_server.serve_forever)
        mock_server_thread.setDaemon(True)
        mock_server_thread.start()

def get_free_port():
    s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    address, port = s.getsockname()
    s.close()
    return port

port = get_free_port()
TestMockServer.run_server(port)
FLOAT_API_KEY = get_float_key('float-key')
FLOAT_API_URL_BASE = 'http://localhost:{}'.format(port)
FLOAT_API_HEADER = None
