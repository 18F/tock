from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

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
