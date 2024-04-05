# annother method i think, by setting your own remote server
#ave this code in a file named remote_server.py and run it. It will start a simple HTTP server on port 8000, responding with "Hello, world!" to any GET requests it receives.

#Once the remote server is running, you can then run your proxy server script. Ensure both scripts are running simultaneously.

#To test the proxy server, you can use any web browser or curl command to make HTTP requests to localhost:8888. The proxy server should forward these requests to the remote server and return the response back to the client.

#Please note that this proxy server is very basic and doesn't handle various edge cases or security concerns. It's intended for educational purposes only.

from http.server import HTTPServer, BaseHTTPRequestHandler

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Hello, world!")

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting httpd...')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
