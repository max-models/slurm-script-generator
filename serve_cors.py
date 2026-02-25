from http.server import HTTPServer, SimpleHTTPRequestHandler

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

if __name__ == '__main__':
    import sys
    port = 8890
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    httpd = HTTPServer(('', port), CORSRequestHandler)
    print(f"Serving with CORS on port {port}")
    httpd.serve_forever()